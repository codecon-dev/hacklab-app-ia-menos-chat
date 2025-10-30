import asyncio
import httpx
import logging
from typing import List, Dict, Any
from unidecode import unidecode
from sqlalchemy.orm import Session
from app.models.cidade import Cidade
from app.repositories.cidade_repository import CidadeRepository

logger = logging.getLogger(__name__)

class IBGEService:
    """Service para buscar dados de municípios na API do IBGE"""
    
    BASE_URL = "https://servicodados.ibge.gov.br/api/v1/localidades"
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = CidadeRepository(db)
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def close(self):
        """Fechar o cliente HTTP"""
        await self.client.aclose()
    
    async def get_estados(self) -> List[Dict[str, Any]]:
        """Buscar todos os estados"""
        try:
            response = await self.client.get(f"{self.BASE_URL}/estados")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Erro ao buscar estados: {e}")
            raise
    
    async def get_municipios_por_uf(self, uf: str) -> List[Dict[str, Any]]:
        """Buscar municípios por UF"""
        try:
            response = await self.client.get(f"{self.BASE_URL}/estados/{uf}/municipios")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Erro ao buscar municípios para UF {uf}: {e}")
            raise
    
    def normalizar_nome(self, nome: str) -> str:
        """Normalizar nome da cidade removendo acentos e convertendo para lowercase"""
        return unidecode(nome.lower().strip())
    
    def _gerar_coordenadas_aproximadas(self, uf: str) -> Dict[str, float]:
        """
        Gera coordenadas aproximadas baseadas na UF
        Coordenadas do centro geográfico de cada estado
        """
        coordenadas_por_uf = {
            "AC": {"latitude": -8.77, "longitude": -70.55},   # Acre
            "AL": {"latitude": -9.71, "longitude": -35.73},   # Alagoas  
            "AP": {"latitude": 1.41, "longitude": -51.77},    # Amapá
            "AM": {"latitude": -3.07, "longitude": -61.66},   # Amazonas
            "BA": {"latitude": -12.96, "longitude": -38.51},  # Bahia
            "CE": {"latitude": -3.71, "longitude": -38.54},   # Ceará
            "DF": {"latitude": -15.83, "longitude": -47.86},  # Distrito Federal
            "ES": {"latitude": -19.19, "longitude": -40.34},  # Espírito Santo
            "GO": {"latitude": -16.64, "longitude": -49.31},  # Goiás
            "MA": {"latitude": -2.55, "longitude": -44.30},   # Maranhão
            "MT": {"latitude": -12.64, "longitude": -55.42},  # Mato Grosso
            "MS": {"latitude": -20.51, "longitude": -54.54},  # Mato Grosso do Sul
            "MG": {"latitude": -18.10, "longitude": -44.38},  # Minas Gerais
            "PA": {"latitude": -5.53, "longitude": -52.29},   # Pará
            "PB": {"latitude": -7.06, "longitude": -35.55},   # Paraíba
            "PR": {"latitude": -24.89, "longitude": -51.55},  # Paraná
            "PE": {"latitude": -8.28, "longitude": -35.07},   # Pernambuco
            "PI": {"latitude": -8.28, "longitude": -43.68},   # Piauí
            "RJ": {"latitude": -22.84, "longitude": -43.15},  # Rio de Janeiro
            "RN": {"latitude": -5.22, "longitude": -36.52},   # Rio Grande do Norte
            "RS": {"latitude": -30.01, "longitude": -51.22},  # Rio Grande do Sul
            "RO": {"latitude": -11.22, "longitude": -62.80},  # Rondônia
            "RR": {"latitude": 1.89, "longitude": -61.22},    # Roraima
            "SC": {"latitude": -27.33, "longitude": -49.44},  # Santa Catarina
            "SP": {"latitude": -23.55, "longitude": -46.64},  # São Paulo
            "SE": {"latitude": -10.90, "longitude": -37.07},  # Sergipe
            "TO": {"latitude": -10.25, "longitude": -48.25},  # Tocantins
        }
        
        base = coordenadas_por_uf.get(uf.upper(), {"latitude": -14.235, "longitude": -51.925})
        
        # Adicionar pequena variação aleatória para não sobrepor cidades
        import random
        latitude = base["latitude"] + random.uniform(-0.5, 0.5)
        longitude = base["longitude"] + random.uniform(-0.5, 0.5)
        
        return {"latitude": latitude, "longitude": longitude}
    
    async def popular_cidades_por_uf(self, uf: str) -> Dict[str, Any]:
        """Popular banco de dados com cidades de uma UF"""
        try:
            print(f"🔍 Buscando municípios da UF: {uf}")
            municipios = await self.get_municipios_por_uf(uf.upper())
            
            cidades_inseridas = 0
            cidades_atualizadas = 0
            
            for municipio in municipios:
                nome = municipio.get("nome", "")
                ibge_id = municipio.get("id")
                
                if not nome or not ibge_id:
                    continue
                
                # Verificar se cidade já existe
                cidade_existente = self.repository.get_by_ibge_id(ibge_id)
                
                # Gerar coordenadas aproximadas
                coordenadas = self._gerar_coordenadas_aproximadas(uf)
                
                if cidade_existente:
                    # Atualizar cidade existente se necessário
                    cidades_atualizadas += 1
                else:
                    # Criar nova cidade
                    nova_cidade = Cidade(
                        nome=nome,
                        nome_normalizado=self.normalizar_nome(nome),
                        uf=uf.upper(),
                        latitude=coordenadas["latitude"],
                        longitude=coordenadas["longitude"],
                        ibge_id=ibge_id
                    )
                    self.db.add(nova_cidade)
                    cidades_inseridas += 1
            
            self.db.commit()
            print(f"✅ UF {uf}: {cidades_inseridas} inseridas, {cidades_atualizadas} atualizadas")
            
            return {
                "uf": uf.upper(),
                "cidades_inseridas": cidades_inseridas,
                "cidades_atualizadas": cidades_atualizadas,
                "total": cidades_inseridas + cidades_atualizadas
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao popular cidades da UF {uf}: {e}")
            raise
    
    async def popular_todas_cidades(self) -> Dict[str, Any]:
        """Popular banco de dados com todas as cidades do Brasil"""
        try:
            print("🌎 Iniciando busca de todos os estados...")
            estados = await self.get_estados()
            
            resultado = {
                "estados_processados": 0,
                "total_cidades_inseridas": 0,
                "total_cidades_atualizadas": 0,
                "detalhes": []
            }
            
            for estado in estados:
                uf = estado.get("sigla")
                nome_estado = estado.get("nome")
                
                if uf:
                    try:
                        print(f"📍 Processando {nome_estado} ({uf})...")
                        resultado_uf = await self.popular_cidades_por_uf(uf)
                        resultado["detalhes"].append(resultado_uf)
                        resultado["total_cidades_inseridas"] += resultado_uf["cidades_inseridas"]
                        resultado["total_cidades_atualizadas"] += resultado_uf["cidades_atualizadas"]
                        resultado["estados_processados"] += 1
                        
                        # Pequena pausa para não sobrecarregar a API do IBGE
                        await asyncio.sleep(0.1)
                        
                    except Exception as e:
                        print(f"❌ Erro ao processar UF {uf}: {e}")
                        continue
            
            await self.close()
            print(f"🎉 Processo concluído! {resultado['estados_processados']} estados processados")
            
            return resultado
            
        except Exception as e:
            logger.error(f"Erro ao popular todas as cidades: {e}")
            await self.close()
            raise