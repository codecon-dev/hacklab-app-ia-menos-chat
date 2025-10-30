import google.generativeai as genai
import json
import hashlib
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from app.core.config import settings
from app.schemas.turismo import RotaTuristica, PontoTuristico, CoordenadaGPS
import logging

logger = logging.getLogger(__name__)


class GeminiService:
    """Service para integração com Google Gemini AI com sistema de cache"""

    # Cache estático para compartilhar entre instâncias
    _cache: Dict[str, Dict[str, Any]] = {}
    _cache_ttl = timedelta(hours=24)  # Cache expira em 24 horas

    def __init__(self):
        """Inicializar serviço Gemini"""
        if not settings.GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY não configurada. Configure no arquivo .env"
            )

        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel("gemini-2.5-flash")

    def _gerar_cache_key(
        self,
        cidade_origem: str,
        cidade_destino: str,
        uf_origem: Optional[str] = None,
        uf_destino: Optional[str] = None,
        preferencias: Optional[str] = None,
    ) -> str:
        """Gerar chave única para cache baseada nos parâmetros da consulta"""
        # Normalizar dados para cache
        origem = f"{cidade_origem.lower().strip()}"
        if uf_origem:
            origem += f"-{uf_origem.upper().strip()}"

        destino = f"{cidade_destino.lower().strip()}"
        if uf_destino:
            destino += f"-{uf_destino.upper().strip()}"

        prefs = preferencias.lower().strip() if preferencias else ""

        # Criar string única e gerar hash
        cache_string = f"{origem}|{destino}|{prefs}"
        return hashlib.md5(cache_string.encode()).hexdigest()

    def _limpar_cache_expirado(self):
        """Limpar entradas expiradas do cache"""
        agora = datetime.now()
        keys_expiradas = []

        for key, dados in self._cache.items():
            if agora - dados["timestamp"] > self._cache_ttl:
                keys_expiradas.append(key)

        for key in keys_expiradas:
            del self._cache[key]
            logger.info(f"Cache expirado removido: {key}")

    def _salvar_no_cache(self, cache_key: str, rota: RotaTuristica):
        """Salvar resultado no cache"""
        self._cache[cache_key] = {"rota": rota, "timestamp": datetime.now()}
        logger.info(f"Resultado salvo no cache: {cache_key}")

    def _buscar_no_cache(self, cache_key: str) -> Optional[RotaTuristica]:
        """Buscar resultado no cache"""
        if cache_key in self._cache:
            dados = self._cache[cache_key]

            # Verificar se não expirou
            if datetime.now() - dados["timestamp"] <= self._cache_ttl:
                logger.info(f"Cache hit: {cache_key}")
                return dados["rota"]
            else:
                # Remover entrada expirada
                del self._cache[cache_key]
                logger.info(f"Cache expirado removido: {cache_key}")

        return None

    @classmethod
    def obter_estatisticas_cache(cls) -> Dict[str, Any]:
        """Obter estatísticas do cache"""
        total_entradas = len(cls._cache)
        agora = datetime.now()
        entradas_validas = sum(
            1
            for dados in cls._cache.values()
            if agora - dados["timestamp"] <= cls._cache_ttl
        )

        return {
            "total_entradas": total_entradas,
            "entradas_validas": entradas_validas,
            "entradas_expiradas": total_entradas - entradas_validas,
            "cache_ttl_horas": cls._cache_ttl.total_seconds() / 3600,
        }

    @classmethod
    def limpar_cache(cls):
        """Limpar todo o cache"""
        cls._cache.clear()
        logger.info("Cache completamente limpo")

    def _criar_prompt_turismo(
        self,
        cidade_origem: str,
        cidade_destino: str,
        uf_origem: Optional[str] = None,
        uf_destino: Optional[str] = None,
        preferencias: Optional[str] = None,
    ) -> str:
        """Criar prompt estruturado para consulta turística"""

        origem = f"{cidade_origem}"
        if uf_origem:
            origem += f", {uf_origem}"

        destino = f"{cidade_destino}"
        if uf_destino:
            destino += f", {uf_destino}"

        preferencias_texto = ""
        if preferencias:
            preferencias_texto = f"\nPreferências do usuário: {preferencias}"

        prompt = f"""
            Você é um especialista em turismo brasileiro. Crie uma rota turística detalhada entre duas cidades brasileiras.

            CIDADES:
            - Origem: {origem}
            - Destino: {destino}
            {preferencias_texto}

            INSTRUÇÕES IMPORTANTES:
            1. Responda **EXCLUSIVAMENTE** com um **JSON válido**, sem explicações, comentários, nem texto antes ou depois.
            2. Inclua **pontos turísticos relevantes e acessíveis** tanto nas cidades de origem e destino quanto **ao longo da rota entre elas**.
            3. Todos os pontos turísticos devem ter **coordenadas GPS reais e verificáveis**, compatíveis com o **OpenStreetMap** (ex: https://www.openstreetmap.org/).
            4. Para cada ponto turístico, adicione informações detalhadas e realistas:
            - Descrição do local e destaque cultural/natural.
            - Tempo estimado de visita.
            - Categoria (histórico, natural, cultural, religioso ou gastronômico).
            - Endereço aproximado.
            - Horário de funcionamento (com dias e horários reais ou plausíveis).
            - Valor da entrada (exato ou estimado; use “Gratuito” se aplicável).
            - Dicas práticas (ex: evitar horários de pico, levar protetor solar, usar calçado confortável etc).
            5. Inclua no final:
            - Recomendações gerais para o trajeto (ex: segurança, clima, estrada, paradas).
            - Melhor época para visitar (mês ou estação do ano mais indicada).

            FORMATO JSON OBRIGATÓRIO:
            
            {{
            "cidade_origem": "{origem}",
            "cidade_destino": "{destino}",
            "distancia_aproximada": "XXX km",
            "tempo_viagem_estimado": "X horas de carro",
            "pontos_turisticos": [
                {{
                "nome": "Nome do Ponto Turístico",
                "descricao": "Descrição detalhada e interessante do local",
                "coordenadas": {{
                    "latitude": -23.5505,
                    "longitude": -46.6333
                }},
                "tempo_visita_estimado": "2 horas",
                "categoria": "histórico|natural|cultural|religioso|gastronômico",
                "endereco": "Endereço aproximado",
                "horario_funcionamento": "Seg-Dom 9h às 17h",
                "valor_entrada": "Gratuito ou R$ XX",
                "dicas_importantes": "Dicas úteis para a visita"
                }}
            ],
            "recomendacoes_gerais": "Recomendações gerais para a viagem",
            "melhor_epoca_visita": "Melhor época para visitar a região"
            }}

            REQUISITOS DE QUALIDADE:
            - Use **apenas informações reais e verificáveis** (sem locais fictícios).
            - As coordenadas devem funcionar **corretamente no OpenStreetMap**.
            - Cada atração deve ser **única e bem descrita**.
            - Não inclua hospedagem, restaurantes ou rodovias — apenas **atrações turísticas**.
            - A resposta deve ser **um único JSON válido**, sem texto fora das chaves.
            """
        return prompt

    async def consultar_rota_turistica(
        self,
        cidade_origem: str,
        cidade_destino: str,
        uf_origem: Optional[str] = None,
        uf_destino: Optional[str] = None,
        preferencias: Optional[str] = None,
    ) -> RotaTuristica:
        """
        Consultar Gemini para obter rota turística (com cache)

        Args:
            cidade_origem: Nome da cidade de origem
            cidade_destino: Nome da cidade de destino
            uf_origem: UF da cidade origem (opcional)
            uf_destino: UF da cidade destino (opcional)
            preferencias: Preferências de turismo (opcional)

        Returns:
            RotaTuristica: Dados estruturados da rota turística

        Raises:
            Exception: Se houver erro na consulta ou parsing JSON
        """

        try:
            logger.info(
                f"Consultando rota turística: {cidade_origem} → {cidade_destino}"
            )

            # Gerar chave do cache
            cache_key = self._gerar_cache_key(
                cidade_origem=cidade_origem,
                cidade_destino=cidade_destino,
                uf_origem=uf_origem,
                uf_destino=uf_destino,
                preferencias=preferencias,
            )

            # Limpar cache expirado
            self._limpar_cache_expirado()

            # Tentar buscar no cache primeiro
            rota_cache = self._buscar_no_cache(cache_key)
            if rota_cache:
                logger.info(f"🚀 Resposta do cache (instantânea): {cache_key[:8]}...")
                return rota_cache

            # Se não encontrou no cache, consultar Gemini
            logger.info(f"🤖 Consultando Gemini (primeira vez): {cache_key[:8]}...")

            # Criar prompt estruturado
            prompt = self._criar_prompt_turismo(
                cidade_origem=cidade_origem,
                cidade_destino=cidade_destino,
                uf_origem=uf_origem,
                uf_destino=uf_destino,
                preferencias=preferencias,
            )

            # Consultar Gemini
            response = await self._consultar_gemini_async(prompt)

            # Parsing do JSON
            rota_data = self._parse_response_json(response)

            # Validar e criar objeto Pydantic
            rota = self._criar_rota_turistica(rota_data)

            # Salvar no cache
            self._salvar_no_cache(cache_key, rota)

            logger.info(
                f"Rota turística criada com {len(rota.pontos_turisticos)} pontos"
            )
            return rota

        except Exception as e:
            logger.error(f"Erro ao consultar rota turística: {e}")
            raise Exception(f"Erro na consulta ao Gemini: {str(e)}")

    async def _consultar_gemini_async(self, prompt: str) -> str:
        """Consulta assíncrona ao Gemini"""
        try:
            response = self.model.generate_content(prompt)

            if not response or not response.text:
                raise Exception("Resposta vazia do Gemini")

            return response.text.strip()

        except Exception as e:
            logger.error(f"Erro na consulta ao Gemini: {e}")
            raise Exception(f"Falha na comunicação com Gemini: {str(e)}")

    def _parse_response_json(self, response_text: str) -> Dict[str, Any]:
        """Parse da resposta JSON do Gemini"""
        try:
            # Limpar possível texto extra
            response_clean = response_text.strip()

            # Remover markdown se presente
            if response_clean.startswith("```json"):
                response_clean = response_clean[7:]
            if response_clean.endswith("```"):
                response_clean = response_clean[:-3]

            response_clean = response_clean.strip()

            # Parse JSON
            data = json.loads(response_clean)

            if not isinstance(data, dict):
                raise ValueError("Resposta não é um objeto JSON válido")

            return data

        except json.JSONDecodeError as e:
            logger.error(f"Erro no parsing JSON: {e}")
            logger.error(f"Resposta recebida: {response_text[:500]}...")
            raise Exception(f"Resposta do Gemini não é um JSON válido: {str(e)}")

    def _criar_rota_turistica(self, data: Dict[str, Any]) -> RotaTuristica:
        """Criar objeto RotaTuristica a partir dos dados"""
        try:
            # Validar campos obrigatórios
            if "pontos_turisticos" not in data:
                data["pontos_turisticos"] = []

            # Processar pontos turísticos
            pontos_turisticos = []
            for ponto_data in data.get("pontos_turisticos", []):
                try:
                    # Criar coordenadas
                    coord_data = ponto_data.get("coordenadas", {})
                    coordenadas = CoordenadaGPS(
                        latitude=coord_data.get("latitude", 0.0),
                        longitude=coord_data.get("longitude", 0.0),
                    )

                    # Criar ponto turístico
                    ponto = PontoTuristico(
                        nome=ponto_data.get("nome", "Nome não informado"),
                        descricao=ponto_data.get(
                            "descricao", "Descrição não disponível"
                        ),
                        coordenadas=coordenadas,
                        tempo_visita_estimado=ponto_data.get(
                            "tempo_visita_estimado", "Não informado"
                        ),
                        categoria=ponto_data.get("categoria", "geral"),
                        endereco=ponto_data.get("endereco"),
                        horario_funcionamento=ponto_data.get("horario_funcionamento"),
                        valor_entrada=ponto_data.get("valor_entrada"),
                        dicas_importantes=ponto_data.get("dicas_importantes"),
                    )

                    pontos_turisticos.append(ponto)

                except Exception as e:
                    logger.warning(f"Erro ao processar ponto turístico: {e}")
                    continue

            # Criar rota turística
            rota = RotaTuristica(
                cidade_origem=data.get("cidade_origem", "Não informado"),
                cidade_destino=data.get("cidade_destino", "Não informado"),
                distancia_aproximada=data.get("distancia_aproximada"),
                tempo_viagem_estimado=data.get("tempo_viagem_estimado"),
                pontos_turisticos=pontos_turisticos,
                recomendacoes_gerais=data.get("recomendacoes_gerais"),
                melhor_epoca_visita=data.get("melhor_epoca_visita"),
            )

            return rota

        except Exception as e:
            logger.error(f"Erro ao criar RotaTuristica: {e}")
            raise Exception(f"Erro ao processar dados da rota: {str(e)}")
