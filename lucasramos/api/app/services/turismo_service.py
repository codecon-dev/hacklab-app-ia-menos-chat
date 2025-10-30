from typing import Optional
from sqlalchemy.orm import Session
from app.repositories.cidade_repository import CidadeRepository
from app.services.gemini_service import GeminiService
from app.schemas.turismo import SolicitacaoRota, RespostaTurismo, RotaTuristica
from app.models.cidade import Cidade
import logging

logger = logging.getLogger(__name__)

class TurismoService:
    """Service principal para funcionalidades de turismo"""
    
    def __init__(self, db: Session):
        """
        Inicializar serviço de turismo
        
        Args:
            db: Sessão do banco de dados
        """
        self.db = db
        self.cidade_repository = CidadeRepository(db)
        self.gemini_service = GeminiService()
    
    async def obter_rota_turistica(self, solicitacao: SolicitacaoRota) -> RespostaTurismo:
        """
        Obter rota turística entre duas cidades
        
        Args:
            solicitacao: Dados da solicitação de rota
            
        Returns:
            RespostaTurismo: Resposta com a rota turística ou erro
        """
        
        try:
            logger.info(f"Processando rota: {solicitacao.cidade_origem} → {solicitacao.cidade_destino}")
            
            # Buscar e validar cidades no banco
            cidade_origem = await self._buscar_cidade(
                solicitacao.cidade_origem, 
                solicitacao.uf_origem
            )
            
            cidade_destino = await self._buscar_cidade(
                solicitacao.cidade_destino, 
                solicitacao.uf_destino
            )
            
            # Verificar se as cidades são diferentes
            if (cidade_origem and cidade_destino and 
                cidade_origem.nome.lower() == cidade_destino.nome.lower() and
                str(cidade_origem.uf) == str(cidade_destino.uf)):
                return RespostaTurismo(
                    sucesso=False,
                    erro="As cidades de origem e destino não podem ser iguais",
                    rota=None,
                    metadata=None
                )
            
            # Obter UFs das cidades encontradas ou usar as fornecidas
            uf_origem = str(cidade_origem.uf) if cidade_origem else solicitacao.uf_origem
            uf_destino = str(cidade_destino.uf) if cidade_destino else solicitacao.uf_destino
            
            # Consultar Gemini para obter rota turística
            rota = await self.gemini_service.consultar_rota_turistica(
                cidade_origem=solicitacao.cidade_origem,
                cidade_destino=solicitacao.cidade_destino,
                uf_origem=uf_origem,
                uf_destino=uf_destino,
                preferencias=solicitacao.preferencias
            )
            
            # Criar metadados da consulta
            metadata = {
                "cidades_encontradas_bd": {
                    "origem": cidade_origem.nome if cidade_origem else None,
                    "destino": cidade_destino.nome if cidade_destino else None
                },
                "total_pontos_turisticos": len(rota.pontos_turisticos),
                "consulta_gemini": True
            }
            
            return RespostaTurismo(
                sucesso=True,
                rota=rota,
                erro=None,
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Erro ao obter rota turística: {e}")
            return RespostaTurismo(
                sucesso=False,
                erro=f"Erro interno: {str(e)}",
                rota=None,
                metadata=None
            )
    
    async def _buscar_cidade(self, nome_cidade: str, uf: Optional[str] = None) -> Optional[Cidade]:
        """
        Buscar cidade no banco de dados
        
        Args:
            nome_cidade: Nome da cidade
            uf: UF da cidade (opcional)
            
        Returns:
            Cidade encontrada ou None
        """
        
        try:
            # Primeiro, tentar busca exata com UF se fornecida
            if uf:
                cidade = self.cidade_repository.get_by_nome(nome_cidade, uf.upper())
                if cidade:
                    logger.info(f"Cidade encontrada no BD: {cidade.nome}, {cidade.uf}")
                    return cidade
            
            # Busca por nome sem UF
            cidade = self.cidade_repository.get_by_nome(nome_cidade)
            
            if cidade:
                logger.info(f"Cidade encontrada no BD: {cidade.nome}, {cidade.uf}")
                return cidade
            
            logger.info(f"Cidade não encontrada no BD: {nome_cidade}")
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar cidade {nome_cidade}: {e}")
            return None
    
    async def listar_cidades_disponiveis(self, uf: Optional[str] = None, 
                                       limite: int = 50, 
                                       offset: int = 0) -> dict:
        """
        Listar cidades disponíveis no banco
        
        Args:
            uf: UF para filtrar (opcional)
            limite: Limite de registros
            offset: Offset para paginação
            
        Returns:
            Dict com cidades e informações de paginação
        """
        
        try:
            if uf:
                cidades = self.cidade_repository.get_all(skip=offset, limit=limite, uf=uf.upper())
                total = self.cidade_repository.count_all(uf=uf.upper())
            else:
                cidades = self.cidade_repository.get_all(skip=offset, limit=limite)
                total = self.cidade_repository.count_all()
            
            return {
                "cidades": [
                    {
                        "nome": cidade.nome,
                        "uf": cidade.uf,
                        "ibge_id": cidade.ibge_id
                    }
                    for cidade in cidades
                ],
                "total": total,
                "limite": limite,
                "offset": offset,
                "tem_proxima_pagina": (offset + limite) < total
            }
            
        except Exception as e:
            logger.error(f"Erro ao listar cidades: {e}")
            raise Exception(f"Erro ao listar cidades: {str(e)}")
    
    async def estatisticas_banco(self) -> dict:
        """
        Obter estatísticas do banco de cidades
        
        Returns:
            Dict com estatísticas
        """
        
        try:
            total_cidades = self.cidade_repository.count_all()
            
            # Contar por UF
            ufs_stats = {}
            for uf in ['AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 
                      'MA', 'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 
                      'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO']:
                count = self.cidade_repository.count_all(uf=uf)
                if count > 0:
                    ufs_stats[uf] = count
            
            return {
                "total_cidades": total_cidades,
                "total_ufs_com_dados": len(ufs_stats),
                "cidades_por_uf": ufs_stats
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
            raise Exception(f"Erro ao obter estatísticas: {str(e)}")