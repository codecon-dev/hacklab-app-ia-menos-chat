"""
Schemas Pydantic para Roteiros
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class RoteiroBase(BaseModel):
    """Schema base para roteiro"""
    titulo: str = Field(..., min_length=1, max_length=255, description="Título do roteiro")
    origem: str = Field(..., min_length=1, max_length=255, description="Cidade de origem")
    destino: str = Field(..., min_length=1, max_length=255, description="Cidade de destino")
    preferencias: Optional[str] = Field(None, description="Preferências do usuário")

class RoteiroCreate(RoteiroBase):
    """Schema para criação de roteiro"""
    conteudo: str = Field(..., min_length=1, description="Conteúdo gerado pela IA")
    pontos_json: Optional[str] = Field(None, description="JSON com coordenadas dos pontos turísticos")

class RoteiroUpdate(BaseModel):
    """Schema para atualização de roteiro"""
    titulo: Optional[str] = Field(None, min_length=1, max_length=255)
    preferencias: Optional[str] = None

class RoteiroResponse(RoteiroBase):
    """Schema de resposta para roteiro"""
    id: int
    conteudo: str
    pontos_json: Optional[str] = None
    usuario_id: int
    data_criacao: datetime
    data_atualizacao: datetime

    class Config:
        from_attributes = True

class RoteiroListResponse(BaseModel):
    """Schema para listagem de roteiros"""
    id: int
    titulo: str
    origem: str
    destino: str
    data_criacao: datetime
    data_atualizacao: datetime

    class Config:
        from_attributes = True

class RoteiroSaveRequest(BaseModel):
    """Schema para salvar roteiro a partir da busca atual"""
    titulo: str = Field(..., min_length=1, max_length=255, description="Título para o roteiro")
    origem: str = Field(..., min_length=1, max_length=255, description="Cidade de origem")
    destino: str = Field(..., min_length=1, max_length=255, description="Cidade de destino")
    preferencias: Optional[str] = Field(None, description="Preferências do usuário")
    conteudo: str = Field(..., min_length=1, description="Conteúdo gerado pela IA")
    pontos: Optional[List[Dict[str, Any]]] = Field(None, description="Lista de pontos turísticos com coordenadas")