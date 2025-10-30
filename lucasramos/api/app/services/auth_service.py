from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.usuario import LoginRequest, CadastroRequest, UsuarioCreate
import secrets
import string

class AuthService:
    """Service para operações de autenticação"""
    
    SENHA_FIXA = "sejapro"  # Senha fixa para todos os usuários
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = UsuarioRepository(db)
    
    def fazer_login(self, login_data: LoginRequest) -> Dict[str, Any]:
        """
        Realizar login do usuário
        
        Args:
            login_data: Dados de login (email e senha)
            
        Returns:
            Dict com resultado do login
        """
        # Verificar se a senha está correta
        if login_data.senha != self.SENHA_FIXA:
            return {
                "success": False,
                "message": "Senha incorreta. A senha padrão é 'sejapro'.",
                "usuario": None,
                "token": None
            }
        
        # Buscar usuário por email
        usuario = self.repository.get_by_email(login_data.email)
        
        if not usuario:
            return {
                "success": False,
                "message": "Usuário não encontrado. Faça seu cadastro primeiro.",
                "usuario": None,
                "token": None
            }
        
        if not usuario.ativo:
            return {
                "success": False,
                "message": "Usuário desativado. Entre em contato com o administrador.",
                "usuario": None,
                "token": None
            }
        
        # Atualizar último login
        self.repository.update_ultimo_login(usuario.id)
        
        # Gerar token simples
        token = self._gerar_token_simples(usuario.id)
        
        return {
            "success": True,
            "message": f"Login realizado com sucesso! Bem-vindo(a), {usuario.nome}!",
            "usuario": {
                "id": usuario.id,
                "nome": usuario.nome,
                "email": usuario.email,
                "ativo": usuario.ativo,
                "ultimo_login": usuario.ultimo_login,
                "created_at": usuario.created_at
            },
            "token": token
        }
    
    def fazer_cadastro(self, cadastro_data: CadastroRequest) -> Dict[str, Any]:
        """
        Realizar cadastro de novo usuário
        
        Args:
            cadastro_data: Dados de cadastro
            
        Returns:
            Dict com resultado do cadastro
        """
        # Verificar se a senha está correta
        if cadastro_data.senha != self.SENHA_FIXA:
            return {
                "success": False,
                "message": f"Senha incorreta. A senha padrão é '{self.SENHA_FIXA}'.",
                "usuario": None
            }
        
        # Verificar se email já existe
        if self.repository.existe_email(cadastro_data.email):
            return {
                "success": False,
                "message": "Email já cadastrado. Faça login ou use outro email.",
                "usuario": None
            }
        
        # Criar usuário
        try:
            usuario_create = UsuarioCreate(
                nome=cadastro_data.nome,
                email=cadastro_data.email.lower()
            )
            
            usuario = self.repository.create(usuario_create)
            
            return {
                "success": True,
                "message": f"Cadastro realizado com sucesso! Bem-vindo(a), {usuario.nome}!",
                "usuario": {
                    "id": usuario.id,
                    "nome": usuario.nome,
                    "email": usuario.email,
                    "ativo": usuario.ativo,
                    "ultimo_login": usuario.ultimo_login,
                    "created_at": usuario.created_at
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Erro ao criar usuário: {str(e)}",
                "usuario": None
            }
    
    def verificar_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verificar se token é válido (implementação simples)
        
        Args:
            token: Token a ser verificado
            
        Returns:
            Dados do usuário se token válido, None caso contrário
        """
        try:
            # Extrair ID do usuário do token (implementação simples)
            if token.startswith("user_"):
                user_id_str = token.replace("user_", "").split("_")[0]
                user_id = int(user_id_str)
                
                usuario = self.repository.get_by_id(user_id)
                
                if usuario and usuario.ativo:
                    return {
                        "id": usuario.id,
                        "nome": usuario.nome,
                        "email": usuario.email,
                        "ativo": usuario.ativo
                    }
        except:
            pass
        
        return None
    
    def listar_usuarios(self, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """
        Listar usuários com paginação
        
        Args:
            page: Número da página
            per_page: Itens por página
            
        Returns:
            Dict com usuários paginados
        """
        offset = (page - 1) * per_page
        usuarios = self.repository.get_all(skip=offset, limit=per_page)
        total = self.repository.count_all()
        total_pages = (total + per_page - 1) // per_page
        
        usuarios_lista = []
        for usuario in usuarios:
            usuarios_lista.append({
                "id": usuario.id,
                "nome": usuario.nome,
                "email": usuario.email,
                "ativo": usuario.ativo,
                "ultimo_login": usuario.ultimo_login,
                "created_at": usuario.created_at
            })
        
        return {
            "usuarios": usuarios_lista,
            "pagination": {
                "current_page": page,
                "per_page": per_page,
                "total_items": total,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        }
    
    def _gerar_token_simples(self, user_id: int) -> str:
        """Gerar token simples para o usuário"""
        random_part = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(16))
        return f"user_{user_id}_{random_part}"