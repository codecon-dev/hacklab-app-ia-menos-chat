from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

class LoginRequest(BaseModel):
    """Schema para requisição de login"""
    email: EmailStr = Field(..., description="Email do usuário")
    senha: str = Field(..., min_length=1, description="Senha do usuário")

class UsuarioCreate(BaseModel):
    """Schema para criação de usuário"""
    nome: str = Field(..., min_length=2, max_length=100, description="Nome completo do usuário")
    email: EmailStr = Field(..., description="Email do usuário")

class UsuarioResponse(BaseModel):
    """Schema para resposta de usuário"""
    id: int = Field(..., description="ID do usuário")
    nome: str = Field(..., description="Nome do usuário")
    email: str = Field(..., description="Email do usuário")
    ativo: bool = Field(..., description="Se o usuário está ativo")
    ultimo_login: Optional[datetime] = Field(None, description="Data do último login")
    created_at: datetime = Field(..., description="Data de criação")

    class Config:
        from_attributes = True

class LoginResponse(BaseModel):
    """Schema para resposta de login"""
    success: bool = Field(..., description="Se o login foi bem-sucedido")
    message: str = Field(..., description="Mensagem de retorno")
    usuario: Optional[UsuarioResponse] = Field(None, description="Dados do usuário logado")
    token: Optional[str] = Field(None, description="Token de autenticação")

class CadastroRequest(BaseModel):
    """Schema para cadastro de novo usuário"""
    nome: str = Field(..., min_length=2, max_length=100, description="Nome completo")
    email: EmailStr = Field(..., description="Email para login")
    senha: str = Field(..., min_length=1, description="Senha (sempre 'sejapro')")

class CadastroResponse(BaseModel):
    """Schema para resposta de cadastro"""
    success: bool = Field(..., description="Se o cadastro foi bem-sucedido")
    message: str = Field(..., description="Mensagem de retorno")
    usuario: Optional[UsuarioResponse] = Field(None, description="Dados do usuário criado")