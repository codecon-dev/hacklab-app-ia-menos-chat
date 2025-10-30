"""
Rotas para gerenciamento de Roteiros Salvos
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query, Header
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.auth_service import AuthService
from app.services.roteiro_service import RoteiroService
from app.schemas.roteiro import (
    RoteiroSaveRequest,
    RoteiroResponse, 
    RoteiroListResponse, 
    RoteiroUpdate
)

router = APIRouter()

def get_current_user_id(
    authorization: str = Header(...),
    db: Session = Depends(get_db)
) -> int:
    """Dependency para obter ID do usuário atual do token"""
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autorização inválido"
        )
    
    token = authorization.replace("Bearer ", "")
    auth_service = AuthService(db)
    user_data = auth_service.verificar_token(token)
    
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado ou inválido"
        )
    
    return user_data["id"]

@router.post("/", response_model=RoteiroResponse, status_code=status.HTTP_201_CREATED)
def salvar_roteiro(
    roteiro_request: RoteiroSaveRequest,
    db: Session = Depends(get_db),
    usuario_id: int = Depends(get_current_user_id)
):
    """
    Salvar novo roteiro do usuário
    """
    service = RoteiroService(db)
    return service.salvar_roteiro(roteiro_request, usuario_id)

@router.get("/", response_model=List[RoteiroListResponse])
def listar_roteiros(
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(100, ge=1, le=100, description="Número máximo de registros"),
    db: Session = Depends(get_db),
    usuario_id: int = Depends(get_current_user_id)
):
    """
    Listar roteiros salvos do usuário
    """
    service = RoteiroService(db)
    return service.listar_roteiros(usuario_id, skip, limit)

@router.get("/buscar", response_model=List[RoteiroListResponse])
def buscar_roteiros(
    titulo: str = Query(..., min_length=1, description="Texto para buscar no título"),
    db: Session = Depends(get_db),
    usuario_id: int = Depends(get_current_user_id)
):
    """
    Buscar roteiros por título
    """
    service = RoteiroService(db)
    return service.buscar_roteiros(usuario_id, titulo)

@router.get("/estatisticas")
def estatisticas_roteiros(
    db: Session = Depends(get_db),
    usuario_id: int = Depends(get_current_user_id)
):
    """
    Obter estatísticas dos roteiros do usuário
    """
    service = RoteiroService(db)
    return service.estatisticas_usuario(usuario_id)

@router.get("/{roteiro_id}", response_model=RoteiroResponse)
def obter_roteiro(
    roteiro_id: int,
    db: Session = Depends(get_db),
    usuario_id: int = Depends(get_current_user_id)
):
    """
    Obter roteiro específico
    """
    service = RoteiroService(db)
    return service.obter_roteiro(roteiro_id, usuario_id)

@router.get("/{roteiro_id}/completo")
def obter_roteiro_completo(
    roteiro_id: int,
    db: Session = Depends(get_db),
    usuario_id: int = Depends(get_current_user_id)
):
    """
    Obter roteiro com pontos turísticos parseados
    """
    service = RoteiroService(db)
    return service.obter_roteiro_com_pontos(roteiro_id, usuario_id)

@router.put("/{roteiro_id}", response_model=RoteiroResponse)
def atualizar_roteiro(
    roteiro_id: int,
    roteiro_update: RoteiroUpdate,
    db: Session = Depends(get_db),
    usuario_id: int = Depends(get_current_user_id)
):
    """
    Atualizar roteiro
    """
    service = RoteiroService(db)
    return service.atualizar_roteiro(roteiro_id, usuario_id, roteiro_update)

@router.delete("/{roteiro_id}")
def deletar_roteiro(
    roteiro_id: int,
    db: Session = Depends(get_db),
    usuario_id: int = Depends(get_current_user_id)
):
    """
    Deletar roteiro
    """
    service = RoteiroService(db)
    return service.deletar_roteiro(roteiro_id, usuario_id)