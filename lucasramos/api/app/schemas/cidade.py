from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class CidadeBase(BaseModel):
    nome: str = Field(..., description="Nome da cidade")
    uf: str = Field(..., max_length=2, description="Estado (UF)")
    latitude: float = Field(..., description="Latitude")
    longitude: float = Field(..., description="Longitude")

class CidadeCreate(CidadeBase):
    nome_normalizado: Optional[str] = None
    ibge_id: Optional[int] = None

class CidadeUpdate(BaseModel):
    nome: Optional[str] = None
    uf: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class CidadeResponse(CidadeBase):
    id: int
    nome_normalizado: str
    ibge_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CidadeAutocomplete(BaseModel):
    """Schema para resposta de autocomplete de cidades"""
    id: int = Field(..., description="ID da cidade")
    nome: str = Field(..., description="Nome da cidade")
    uf: str = Field(..., description="Estado (UF)")
    latitude: float = Field(..., description="Latitude")
    longitude: float = Field(..., description="Longitude")
    nome_completo: str = Field(..., description="Nome completo (Cidade, UF)")
    ibge_id: Optional[int] = Field(None, description="ID do IBGE")

class AutocompleteResponse(BaseModel):
    """Schema para resposta do endpoint de autocomplete"""
    cidades: List[CidadeAutocomplete] = Field(..., description="Lista de cidades encontradas")
    total: int = Field(..., description="Total de cidades encontradas")
    termo_busca: str = Field(..., description="Termo usado na busca")
    limit: int = Field(..., description="Limite aplicado na busca")
    message: Optional[str] = Field(None, description="Mensagem adicional")

class PontoTuristicoBase(BaseModel):
    nome: str = Field(..., description="Nome do ponto turístico")
    descricao: Optional[str] = Field(None, description="Descrição do ponto turístico")
    latitude: float = Field(..., description="Latitude")
    longitude: float = Field(..., description="Longitude")
    categoria: Optional[str] = Field(None, description="Categoria do ponto turístico")

class PontoTuristicoCreate(PontoTuristicoBase):
    cidade_id: Optional[int] = None

class PontoTuristicoResponse(PontoTuristicoBase):
    id: int
    cidade_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class RotaTuristicaRequest(BaseModel):
    cidade_origem: str = Field(..., description="Nome da cidade de origem")
    cidade_destino: str = Field(..., description="Nome da cidade de destino")
    uf_origem: Optional[str] = Field(None, description="UF da cidade de origem")
    uf_destino: Optional[str] = Field(None, description="UF da cidade de destino")
    preferencias: Optional[list[str]] = Field(default=[], description="Preferências de tipos de pontos turísticos")

class RotaTuristicaResponse(BaseModel):
    cidade_origem: CidadeResponse
    cidade_destino: CidadeResponse
    distancia_km: float
    pontos_turisticos_rota: list[PontoTuristicoResponse]
    sugestoes_ia: str
    tempo_estimado_viagem: Optional[str] = None