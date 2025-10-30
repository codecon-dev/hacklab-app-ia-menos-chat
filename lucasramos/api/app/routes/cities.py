from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.cidade_service import CidadeService
from app.schemas.cidade import AutocompleteResponse

router = APIRouter()

@router.get("/")
async def listar_cidades(
    page: int = Query(1, ge=1, description="Número da página"),
    db: Session = Depends(get_db)
):
    """Listar cidades com paginação de 50 itens por página"""
    service = CidadeService(db)
    resultado = service.listar_cidades_paginadas(page=page, per_page=50)
    return resultado

@router.get("/search", response_model=AutocompleteResponse)
async def buscar_cidades_autocomplete(
    q: str = Query(..., min_length=2, description="Termo de busca (mínimo 2 caracteres)"),
    limit: int = Query(10, ge=1, le=50, description="Limite de resultados (máximo 50)"),
    db: Session = Depends(get_db)
):
    """
    Buscar cidades para autocomplete
    
    - **q**: Termo de busca (nome da cidade)
    - **limit**: Número máximo de resultados (padrão: 10, máximo: 50)
    
    Retorna uma lista de cidades que começam com o termo informado.
    Se não encontrar resultados, busca cidades que contenham o termo.
    
    **Exemplo de uso:**
    ```
    GET /api/v1/cities/search?q=rio&limit=5
    GET /api/v1/cities/search?q=são paulo&limit=10
    ```
    """
    service = CidadeService(db)
    resultado = service.buscar_cidades_autocomplete(termo=q, limit=limit)
    return resultado