"""
Service para lógica de negócios dos Roteiros
"""
import json
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.roteiro import Roteiro
from app.repositories.roteiro_repository import RoteiroRepository
from app.schemas.roteiro import (
    RoteiroCreate, 
    RoteiroUpdate, 
    RoteiroResponse, 
    RoteiroListResponse,
    RoteiroSaveRequest
)

class RoteiroService:
    """Service para gerenciar roteiros salvos"""

    def __init__(self, db: Session):
        self.db = db
        self.repository = RoteiroRepository(db)

    def salvar_roteiro(self, roteiro_request: RoteiroSaveRequest, usuario_id: int) -> RoteiroResponse:
        """Salvar novo roteiro"""
        
        # Preparar dados dos pontos como JSON
        pontos_json = None
        if roteiro_request.pontos:
            try:
                pontos_json = json.dumps(roteiro_request.pontos, ensure_ascii=False)
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Erro ao processar pontos turísticos: {str(e)}"
                )

        # Criar dados do roteiro
        roteiro_data = RoteiroCreate(
            titulo=roteiro_request.titulo,
            origem=roteiro_request.origem,
            destino=roteiro_request.destino,
            preferencias=roteiro_request.preferencias,
            conteudo=roteiro_request.conteudo,
            pontos_json=pontos_json
        )

        # Verificar se já existe roteiro com mesmo título
        existing = self.repository.search_by_title(usuario_id, roteiro_request.titulo)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe um roteiro com este título. Escolha outro nome."
            )

        try:
            roteiro = self.repository.create(roteiro_data, usuario_id)
            return RoteiroResponse.model_validate(roteiro)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao salvar roteiro: {str(e)}"
            )

    def listar_roteiros(self, usuario_id: int, skip: int = 0, limit: int = 100) -> List[RoteiroListResponse]:
        """Listar roteiros do usuário"""
        roteiros = self.repository.get_by_user(usuario_id, skip, limit)
        return [RoteiroListResponse.model_validate(roteiro) for roteiro in roteiros]

    def obter_roteiro(self, roteiro_id: int, usuario_id: int) -> RoteiroResponse:
        """Obter roteiro específico"""
        roteiro = self.repository.get_by_id(roteiro_id, usuario_id)
        if not roteiro:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Roteiro não encontrado"
            )
        
        return RoteiroResponse.model_validate(roteiro)

    def obter_roteiro_com_pontos(self, roteiro_id: int, usuario_id: int) -> Dict[str, Any]:
        """Obter roteiro com pontos parseados"""
        roteiro = self.repository.get_by_id(roteiro_id, usuario_id)
        if not roteiro:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Roteiro não encontrado"
            )

        # Converter para response
        roteiro_response = RoteiroResponse.model_validate(roteiro)
        
        # Adicionar pontos parseados
        pontos = self.repository.get_pontos_parsed(roteiro)
        
        return {
            **roteiro_response.model_dump(),
            "pontos": pontos or []
        }

    def atualizar_roteiro(self, roteiro_id: int, usuario_id: int, roteiro_data: RoteiroUpdate) -> RoteiroResponse:
        """Atualizar roteiro"""
        # Verificar se título não conflita (se estiver sendo atualizado)
        if roteiro_data.titulo:
            existing = self.repository.search_by_title_excluding_id(usuario_id, roteiro_data.titulo, roteiro_id)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Já existe outro roteiro com este título. Escolha outro nome."
                )

        roteiro = self.repository.update(roteiro_id, usuario_id, roteiro_data)
        if not roteiro:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Roteiro não encontrado"
            )
        
        return RoteiroResponse.model_validate(roteiro)

    def deletar_roteiro(self, roteiro_id: int, usuario_id: int) -> Dict[str, str]:
        """Deletar roteiro"""
        success = self.repository.delete(roteiro_id, usuario_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Roteiro não encontrado"
            )
        
        return {"message": "Roteiro deletado com sucesso"}

    def buscar_roteiros(self, usuario_id: int, titulo: str) -> List[RoteiroListResponse]:
        """Buscar roteiros por título"""
        roteiros = self.repository.search_by_title(usuario_id, titulo)
        return [RoteiroListResponse.model_validate(roteiro) for roteiro in roteiros]

    def estatisticas_usuario(self, usuario_id: int) -> Dict[str, Any]:
        """Obter estatísticas dos roteiros do usuário"""
        total = self.repository.count_by_user(usuario_id)
        
        return {
            "total_roteiros": total,
            "mensagem": f"Você tem {total} roteiro(s) salvo(s)"
        }