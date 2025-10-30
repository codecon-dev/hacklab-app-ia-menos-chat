from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.auth_service import AuthService
from app.schemas.usuario import (
    LoginRequest, LoginResponse, 
    CadastroRequest, CadastroResponse
)

router = APIRouter()

@router.post("/login", response_model=LoginResponse)
async def fazer_login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Realizar login no sistema
    
    - **email**: Email cadastrado do usuário
    - **senha**: Senha padrão 'sejapro' (igual para todos os usuários)
    
    Retorna token de autenticação em caso de sucesso.
    """
    service = AuthService(db)
    resultado = service.fazer_login(login_data)
    
    if not resultado["success"]:
        raise HTTPException(status_code=401, detail=resultado["message"])
    
    return resultado

@router.post("/cadastro", response_model=CadastroResponse)
async def fazer_cadastro(
    cadastro_data: CadastroRequest,
    db: Session = Depends(get_db)
):
    """
    Cadastrar novo usuário no sistema
    
    - **nome**: Nome completo do usuário
    - **email**: Email único para login
    - **senha**: Deve ser 'sejapro' (senha padrão)
    
    Cria uma nova conta se o email não existir.
    """
    service = AuthService(db)
    resultado = service.fazer_cadastro(cadastro_data)
    
    if not resultado["success"]:
        raise HTTPException(status_code=400, detail=resultado["message"])
    
    return resultado

@router.get("/usuarios")
async def listar_usuarios(
    page: int = 1,
    per_page: int = 20,
    db: Session = Depends(get_db)
):
    """
    Listar usuários cadastrados (para administração)
    
    - **page**: Número da página
    - **per_page**: Usuários por página
    """
    service = AuthService(db)
    resultado = service.listar_usuarios(page=page, per_page=per_page)
    return resultado

@router.post("/verificar-token")
async def verificar_token(
    token: str,
    db: Session = Depends(get_db)
):
    """
    Verificar se token é válido
    
    - **token**: Token de autenticação
    
    Retorna dados do usuário se token válido.
    """
    service = AuthService(db)
    usuario = service.verificar_token(token)
    
    if not usuario:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")
    
    return {
        "valid": True,
        "usuario": usuario
    }