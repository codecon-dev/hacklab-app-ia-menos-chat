"""
Repository para operações com Roteiros
"""
import json
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_

from app.models.roteiro import Roteiro
from app.schemas.roteiro import RoteiroCreate, RoteiroUpdate

class RoteiroRepository:
    """Repository para gerenciar roteiros salvos"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, roteiro_data: RoteiroCreate, usuario_id: int) -> Roteiro:
        """Criar novo roteiro"""
        roteiro = Roteiro(
            titulo=roteiro_data.titulo,
            origem=roteiro_data.origem,
            destino=roteiro_data.destino,
            preferencias=roteiro_data.preferencias,
            conteudo=roteiro_data.conteudo,
            pontos_json=roteiro_data.pontos_json,
            usuario_id=usuario_id
        )
        
        self.db.add(roteiro)
        self.db.commit()
        self.db.refresh(roteiro)
        return roteiro

    def get_by_id(self, roteiro_id: int, usuario_id: int) -> Optional[Roteiro]:
        """Buscar roteiro por ID (apenas do usuário logado)"""
        return self.db.query(Roteiro).filter(
            and_(Roteiro.id == roteiro_id, Roteiro.usuario_id == usuario_id)
        ).first()

    def get_by_user(self, usuario_id: int, skip: int = 0, limit: int = 100) -> List[Roteiro]:
        """Listar roteiros do usuário"""
        return self.db.query(Roteiro).filter(
            Roteiro.usuario_id == usuario_id
        ).order_by(desc(Roteiro.data_atualizacao)).offset(skip).limit(limit).all()

    def update(self, roteiro_id: int, usuario_id: int, roteiro_data: RoteiroUpdate) -> Optional[Roteiro]:
        """Atualizar roteiro"""
        roteiro = self.get_by_id(roteiro_id, usuario_id)
        if not roteiro:
            return None

        update_data = roteiro_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(roteiro, field, value)

        self.db.commit()
        self.db.refresh(roteiro)
        return roteiro

    def delete(self, roteiro_id: int, usuario_id: int) -> bool:
        """Deletar roteiro"""
        roteiro = self.get_by_id(roteiro_id, usuario_id)
        if not roteiro:
            return False

        self.db.delete(roteiro)
        self.db.commit()
        return True

    def count_by_user(self, usuario_id: int) -> int:
        """Contar roteiros do usuário"""
        return self.db.query(Roteiro).filter(Roteiro.usuario_id == usuario_id).count()

    def search_by_title(self, usuario_id: int, titulo: str) -> List[Roteiro]:
        """Buscar roteiros por título"""
        return self.db.query(Roteiro).filter(
            and_(
                Roteiro.usuario_id == usuario_id,
                Roteiro.titulo.ilike(f"%{titulo}%")
            )
        ).order_by(desc(Roteiro.data_atualizacao)).all()

    def search_by_title_excluding_id(self, usuario_id: int, titulo: str, exclude_id: int) -> List[Roteiro]:
        """Buscar roteiros por título excluindo um ID específico"""
        return self.db.query(Roteiro).filter(
            and_(
                Roteiro.usuario_id == usuario_id,
                Roteiro.titulo.ilike(f"%{titulo}%"),
                Roteiro.id != exclude_id
            )
        ).order_by(desc(Roteiro.data_atualizacao)).all()

    def get_pontos_parsed(self, roteiro: Roteiro) -> Optional[List]:
        """Recuperar pontos do JSON parseado"""
        pontos_json = getattr(roteiro, 'pontos_json', None)
        if not pontos_json or pontos_json.strip() == "":
            return None
        
        try:
            return json.loads(pontos_json)
        except json.JSONDecodeError:
            return None