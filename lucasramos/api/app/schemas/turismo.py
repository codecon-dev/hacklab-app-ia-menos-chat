from pydantic import BaseModel, Field
from typing import List, Optional
from decimal import Decimal

class CoordenadaGPS(BaseModel):
    """Coordenadas GPS para localização no OpenStreetMap"""
    latitude: float = Field(..., description="Latitude em graus decimais")
    longitude: float = Field(..., description="Longitude em graus decimais")

class PontoTuristico(BaseModel):
    """Informações detalhadas de um ponto turístico"""
    nome: str = Field(..., description="Nome do ponto turístico")
    descricao: str = Field(..., description="Descrição detalhada do local")
    coordenadas: CoordenadaGPS = Field(..., description="Coordenadas GPS do local")
    tempo_visita_estimado: str = Field(..., description="Tempo estimado de visita (ex: '2 horas', '1 dia')")
    categoria: str = Field(..., description="Categoria do ponto (ex: 'histórico', 'natural', 'cultural')")
    endereco: Optional[str] = Field(None, description="Endereço aproximado se disponível")
    horario_funcionamento: Optional[str] = Field(None, description="Horário de funcionamento se aplicável")
    valor_entrada: Optional[str] = Field(None, description="Informação sobre entrada/custo")
    dicas_importantes: Optional[str] = Field(None, description="Dicas úteis para a visita")

class RotaTuristica(BaseModel):
    """Rota turística completa entre duas cidades"""
    cidade_origem: str = Field(..., description="Nome da cidade de origem")
    cidade_destino: str = Field(..., description="Nome da cidade de destino")
    distancia_aproximada: Optional[str] = Field(None, description="Distância aproximada entre as cidades")
    tempo_viagem_estimado: Optional[str] = Field(None, description="Tempo estimado de viagem")
    pontos_turisticos: List[PontoTuristico] = Field(..., description="Lista de pontos turísticos na rota")
    recomendacoes_gerais: Optional[str] = Field(None, description="Recomendações gerais para a viagem")
    melhor_epoca_visita: Optional[str] = Field(None, description="Melhor época para visitar")

class SolicitacaoRota(BaseModel):
    """Request para solicitar rota turística"""
    cidade_origem: str = Field(..., description="Nome da cidade de origem", min_length=2)
    cidade_destino: str = Field(..., description="Nome da cidade de destino", min_length=2)
    uf_origem: Optional[str] = Field(None, description="UF da cidade origem (ex: SP, RJ)")
    uf_destino: Optional[str] = Field(None, description="UF da cidade destino (ex: SP, RJ)")
    preferencias: Optional[str] = Field(None, description="Preferências de tipo de turismo (ex: 'histórico', 'natureza')")

class RespostaTurismo(BaseModel):
    """Resposta da consulta turística"""
    sucesso: bool = Field(..., description="Indica se a consulta foi bem-sucedida")
    rota: Optional[RotaTuristica] = Field(None, description="Dados da rota turística")
    erro: Optional[str] = Field(None, description="Mensagem de erro se houver")
    metadata: Optional[dict] = Field(None, description="Metadados adicionais da consulta")