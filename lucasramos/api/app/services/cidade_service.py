from typing import Dict, Any
from sqlalchemy.orm import Session
from app.repositories.cidade_repository import CidadeRepository

class CidadeService:
    """Service para operações com cidades seguindo arquitetura em camadas"""
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = CidadeRepository(db)
    
    def listar_cidades_paginadas(self, page: int = 1, per_page: int = 50) -> Dict[str, Any]:
        """
        Listar cidades com paginação
        
        Args:
            page: Número da página (começa em 1)
            per_page: Itens por página
            
        Returns:
            Dict com dados paginados e metadados
        """
        # Calcular offset
        offset = (page - 1) * per_page
        
        # Buscar cidades via repository
        cidades = self.repository.get_all(skip=offset, limit=per_page)
        
        # Contar total de registros
        total = self.repository.count_all()
        
        # Calcular total de páginas
        total_pages = (total + per_page - 1) // per_page
        
        # Preparar resposta
        cidades_lista = []
        for cidade in cidades:
            cidade_data = {
                "id": cidade.id,
                "nome": cidade.nome,
                "uf": cidade.uf,
                "latitude": cidade.latitude,
                "longitude": cidade.longitude,
                "ibge_id": cidade.ibge_id
            }
            
            # Adicionar data se existir
            try:
                if hasattr(cidade, 'created_at'):
                    cidade_data["created_at"] = str(cidade.created_at)
            except:
                cidade_data["created_at"] = None
                
            cidades_lista.append(cidade_data)
        
        return {
            "cidades": cidades_lista,
            "pagination": {
                "current_page": page,
                "per_page": per_page,
                "total_items": total,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1,
                "next_page": page + 1 if page < total_pages else None,
                "prev_page": page - 1 if page > 1 else None
            }
        }
    
    def buscar_cidades_autocomplete(self, termo: str, limit: int = 10) -> Dict[str, Any]:
        """
        Buscar cidades para autocomplete
        
        Args:
            termo: Termo de busca
            limit: Limite de resultados (padrão 10)
            
        Returns:
            Dict com lista de cidades encontradas
        """
        if not termo or len(termo.strip()) < 2:
            return {
                "cidades": [],
                "total": 0,
                "termo_busca": termo,
                "message": "Digite pelo menos 2 caracteres"
            }
        
        # Buscar cidades via repository
        cidades = self.repository.buscar_por_termo(termo, limit)
        
        # Preparar resposta
        cidades_lista = []
        for cidade in cidades:
            cidades_lista.append({
                "id": cidade.id,
                "nome": cidade.nome,
                "uf": cidade.uf,
                "latitude": cidade.latitude,
                "longitude": cidade.longitude,
                "nome_completo": f"{cidade.nome}, {cidade.uf}",
                "ibge_id": cidade.ibge_id
            })
        
        return {
            "cidades": cidades_lista,
            "total": len(cidades_lista),
            "termo_busca": termo,
            "limit": limit
        }