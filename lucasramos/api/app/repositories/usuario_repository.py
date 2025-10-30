from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate
from datetime import datetime

class UsuarioRepository:
    """Repository para operações com usuários"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, usuario: UsuarioCreate) -> Usuario:
        """Criar novo usuário"""
        db_usuario = Usuario(**usuario.dict())
        self.db.add(db_usuario)
        self.db.commit()
        self.db.refresh(db_usuario)
        return db_usuario
    
    def get_by_id(self, usuario_id: int) -> Optional[Usuario]:
        """Buscar usuário por ID"""
        return self.db.query(Usuario).filter(Usuario.id == usuario_id).first()
    
    def get_by_email(self, email: str) -> Optional[Usuario]:
        """Buscar usuário por email"""
        return self.db.query(Usuario).filter(Usuario.email == email.lower()).first()
    
    def get_all(self, skip: int = 0, limit: int = 100, apenas_ativos: bool = True) -> List[Usuario]:
        """Listar usuários"""
        query = self.db.query(Usuario)
        if apenas_ativos:
            query = query.filter(Usuario.ativo == True)
        return query.offset(skip).limit(limit).all()
    
    def update_ultimo_login(self, usuario_id: int) -> Optional[Usuario]:
        """Atualizar último login do usuário"""
        db_usuario = self.get_by_id(usuario_id)
        if db_usuario:
            db_usuario.ultimo_login = datetime.utcnow()
            db_usuario.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(db_usuario)
        return db_usuario
    
    def desativar_usuario(self, usuario_id: int) -> Optional[Usuario]:
        """Desativar usuário"""
        db_usuario = self.get_by_id(usuario_id)
        if db_usuario:
            db_usuario.ativo = False
            db_usuario.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(db_usuario)
        return db_usuario
    
    def ativar_usuario(self, usuario_id: int) -> Optional[Usuario]:
        """Ativar usuário"""
        db_usuario = self.get_by_id(usuario_id)
        if db_usuario:
            db_usuario.ativo = True
            db_usuario.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(db_usuario)
        return db_usuario
    
    def count_all(self, apenas_ativos: bool = True) -> int:
        """Contar total de usuários"""
        query = self.db.query(Usuario)
        if apenas_ativos:
            query = query.filter(Usuario.ativo == True)
        return query.count()
    
    def existe_email(self, email: str) -> bool:
        """Verificar se email já existe"""
        return self.db.query(Usuario).filter(Usuario.email == email.lower()).first() is not None