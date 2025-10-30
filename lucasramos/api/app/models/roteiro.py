"""
Modelo SQLAlchemy para Roteiros Salvos
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base

class Roteiro(Base):
    __tablename__ = "roteiros"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(255), nullable=False)
    origem = Column(String(255), nullable=False)
    destino = Column(String(255), nullable=False)
    preferencias = Column(Text, nullable=True)
    conteudo = Column(Text, nullable=False)  # Conteúdo gerado pela IA
    pontos_json = Column(Text, nullable=True)  # JSON com coordenadas dos pontos
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    data_criacao = Column(DateTime, default=datetime.utcnow)
    data_atualizacao = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamento com usuário
    usuario = relationship("Usuario", back_populates="roteiros")

    def __repr__(self):
        return f"<Roteiro(id={self.id}, titulo='{self.titulo}', origem='{self.origem}', destino='{self.destino}')>"