from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.turismo_service import TurismoService
from app.services.gemini_service import GeminiService
from app.schemas.turismo import SolicitacaoRota, RespostaTurismo
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

def get_turismo_service(db: Session = Depends(get_db)) -> TurismoService:
    """Dependency para obter instância do TurismoService"""
    return TurismoService(db)

@router.post("/route", response_model=RespostaTurismo)
async def obter_rota_turistica(
    solicitacao: SolicitacaoRota,
    turismo_service: TurismoService = Depends(get_turismo_service)
):
    """
    🗺️ Obter rota turística entre duas cidades usando Gemini AI
    
    Este endpoint consulta o Google Gemini para sugerir pontos turísticos
    entre duas cidades brasileiras, incluindo:
    
    - Coordenadas GPS precisas para OpenStreetMap
    - Tempo estimado de visita em cada local
    - Informações detalhadas sobre cada ponto turístico
    - Categorias (histórico, natural, cultural, etc.)
    - Dicas práticas para a viagem
    
    **Exemplo de uso:**
    ```json
    {
        "cidade_origem": "Rio de Janeiro",
        "cidade_destino": "São Paulo",
        "uf_origem": "RJ",
        "uf_destino": "SP",
        "preferencias": "pontos históricos e culturais"
    }
    ```
    """
    
    try:
        logger.info(f"Nova solicitação de rota: {solicitacao.cidade_origem} → {solicitacao.cidade_destino}")
        
        # Validar entrada básica
        if solicitacao.cidade_origem.strip().lower() == solicitacao.cidade_destino.strip().lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="As cidades de origem e destino devem ser diferentes"
            )
        
        # Obter rota turística
        resultado = await turismo_service.obter_rota_turistica(solicitacao)
        
        # Verificar se houve erro
        if not resultado.sucesso:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=resultado.erro or "Erro desconhecido ao processar solicitação"
            )
        
        return resultado
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Erro inesperado na rota turística: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor. Tente novamente mais tarde."
        )

@router.get("/cities")
async def listar_cidades_disponiveis(
    uf: Optional[str] = None,
    page: int = 1,
    size: int = 50,
    turismo_service: TurismoService = Depends(get_turismo_service)
):
    """
    📋 Listar cidades disponíveis no banco de dados
    
    - **uf**: Filtrar por UF específica (ex: SP, RJ, MG)
    - **page**: Página (inicia em 1)
    - **size**: Itens por página (máximo 100)
    
    Retorna lista paginada de cidades cadastradas no sistema.
    """
    
    try:
        # Validar parâmetros
        if page < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Página deve ser maior que zero"
            )
        
        if size < 1 or size > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tamanho da página deve estar entre 1 e 100"
            )
        
        # Calcular offset
        offset = (page - 1) * size
        
        # Listar cidades
        resultado = await turismo_service.listar_cidades_disponiveis(
            uf=uf,
            limite=size,
            offset=offset
        )
        
        return {
            "cidades": resultado["cidades"],
            "paginacao": {
                "page": page,
                "size": size,
                "total": resultado["total"],
                "total_pages": (resultado["total"] + size - 1) // size,
                "has_next": resultado["tem_proxima_pagina"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao listar cidades: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao listar cidades"
        )

@router.get("/stats")
async def estatisticas_banco(
    turismo_service: TurismoService = Depends(get_turismo_service)
):
    """
    📊 Estatísticas do banco de cidades
    
    Retorna informações sobre:
    - Total de cidades cadastradas
    - Número de UFs com dados
    - Distribuição de cidades por UF
    """
    
    try:
        stats = await turismo_service.estatisticas_banco()
        return stats
        
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao obter estatísticas"
        )

@router.get("/cache/stats")
async def estatisticas_cache():
    """
    📊 Estatísticas do cache do Gemini
    
    Retorna informações sobre o cache de consultas:
    - Total de entradas
    - Entradas válidas vs expiradas
    - Tempo de vida do cache
    """
    try:
        stats = GeminiService.obter_estatisticas_cache()
        return {
            "cache_stats": stats,
            "performance": {
                "cache_hit_benefit": "Resposta instantânea vs 3-5 segundos",
                "ttl_configurado": f"{stats['cache_ttl_horas']:.1f} horas"
            }
        }
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas do cache: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao obter estatísticas do cache"
        )

@router.delete("/cache")
async def limpar_cache():
    """
    🧹 Limpar cache do Gemini
    
    Remove todas as entradas do cache, forçando novas consultas ao Gemini.
    Útil para desenvolvimento ou quando quiser respostas atualizadas.
    """
    try:
        GeminiService.limpar_cache()
        return {"message": "✅ Cache limpo com sucesso"}
    except Exception as e:
        logger.error(f"Erro ao limpar cache: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao limpar cache"
        )

@router.get("/")
async def tourism_home():
    """
    🏠 Página inicial do módulo de turismo
    
    Informações sobre recursos disponíveis.
    """
    return {
        "message": "🗺️ API de Turismo Inteligente",
        "descricao": "Consulte pontos turísticos entre cidades brasileiras usando Gemini AI",
        "recursos_disponiveis": [
            {
                "endpoint": "POST /route",
                "descricao": "Obter rota turística entre duas cidades",
                "tecnologia": "Google Gemini AI + Cache inteligente"
            },
            {
                "endpoint": "GET /cities",
                "descricao": "Listar cidades disponíveis no banco"
            },
            {
                "endpoint": "GET /stats",
                "descricao": "Estatísticas do banco de cidades"
            },
            {
                "endpoint": "GET /cache/stats",
                "descricao": "Estatísticas do cache do Gemini"
            },
            {
                "endpoint": "DELETE /cache",
                "descricao": "Limpar cache para forçar novas consultas"
            }
        ],
        "performance": {
            "primeira_consulta": "3-5 segundos (Gemini AI)",
            "consultas_repetidas": "Instantâneo (Cache)",
            "cache_ttl": "24 horas"
        },
        "configuracao_necessaria": [
            "GEMINI_API_KEY no arquivo .env",
            "Banco PostgreSQL com cidades populadas"
        ],
        "exemplo_uso": {
            "metodo": "POST",
            "url": "/api/v1/tourism/route",
            "body": {
                "cidade_origem": "Rio de Janeiro",
                "cidade_destino": "São Paulo",
                "preferencias": "pontos históricos"
            }
        }
    }