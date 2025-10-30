from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.cidade import Cidade, PontoTuristico
from app.schemas.cidade import CidadeCreate, CidadeUpdate, PontoTuristicoCreate

class CidadeRepository:
    """Repository para operações com cidades"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, cidade: CidadeCreate) -> Cidade:
        """Criar nova cidade"""
        db_cidade = Cidade(**cidade.dict())
        self.db.add(db_cidade)
        self.db.commit()
        self.db.refresh(db_cidade)
        return db_cidade
    
    def get_by_id(self, cidade_id: int) -> Optional[Cidade]:
        """Buscar cidade por ID"""
        return self.db.query(Cidade).filter(Cidade.id == cidade_id).first()
    
    def get_by_nome(self, nome: str, uf: Optional[str] = None) -> Optional[Cidade]:
        """Buscar cidade por nome"""
        query = self.db.query(Cidade).filter(Cidade.nome_normalizado == nome.lower())
        if uf:
            query = query.filter(Cidade.uf == uf.upper())
        return query.first()
    
    def get_by_ibge_id(self, ibge_id: int) -> Optional[Cidade]:
        """Buscar cidade por ID do IBGE"""
        return self.db.query(Cidade).filter(Cidade.ibge_id == ibge_id).first()
    
    def get_all(self, skip: int = 0, limit: int = 100, uf: Optional[str] = None) -> List[Cidade]:
        """Listar cidades com paginação"""
        query = self.db.query(Cidade)
        if uf:
            query = query.filter(Cidade.uf == uf.upper())
        return query.offset(skip).limit(limit).all()
    
    def count_all(self, uf: Optional[str] = None) -> int:
        """Contar total de cidades"""
        query = self.db.query(Cidade)
        if uf:
            query = query.filter(Cidade.uf == uf.upper())
        return query.count()
    
    def update(self, cidade_id: int, cidade_update: CidadeUpdate) -> Optional[Cidade]:
        """Atualizar cidade"""
        db_cidade = self.get_by_id(cidade_id)
        if db_cidade:
            for field, value in cidade_update.dict(exclude_unset=True).items():
                setattr(db_cidade, field, value)
            self.db.commit()
            self.db.refresh(db_cidade)
        return db_cidade
    
    def delete(self, cidade_id: int) -> bool:
        """Deletar cidade"""
        db_cidade = self.get_by_id(cidade_id)
        if db_cidade:
            self.db.delete(db_cidade)
            self.db.commit()
            return True
        return False
    
    def buscar_proximas(self, latitude: float, longitude: float, raio_km: float = 50) -> List[Cidade]:
        """Buscar cidades próximas a uma coordenada (simplificado)"""
        # Implementação simplificada usando cálculo de distância euclidiana
        # Em produção, use PostGIS ou similar para cálculos geográficos precisos
        delta = raio_km / 111.0  # Aproximadamente 1 grau = 111 km
        
        return self.db.query(Cidade).filter(
            Cidade.latitude.between(latitude - delta, latitude + delta),
            Cidade.longitude.between(longitude - delta, longitude + delta)
        ).all()
    
    def buscar_por_termo(self, termo: str, limit: int = 10) -> List[Cidade]:
        """Buscar cidades por termo para autocomplete"""
        termo_limpo = termo.strip().lower()
        if not termo_limpo:
            return []
        
        # Busca por nome que comece com o termo ou contenha o termo
        query = self.db.query(Cidade).filter(
            Cidade.nome_normalizado.like(f'{termo_limpo}%')
        ).order_by(
            Cidade.nome.asc()
        ).limit(limit)
        
        resultados = query.all()
        
        # Se não encontrou resultados começando com o termo, busca contendo o termo
        if not resultados:
            query = self.db.query(Cidade).filter(
                Cidade.nome_normalizado.like(f'%{termo_limpo}%')
            ).order_by(
                Cidade.nome.asc()
            ).limit(limit)
            resultados = query.all()
        
        return resultados

class PontoTuristicoRepository:
    """Repository para operações com pontos turísticos"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, ponto: PontoTuristicoCreate) -> PontoTuristico:
        """Criar novo ponto turístico"""
        db_ponto = PontoTuristico(**ponto.dict())
        self.db.add(db_ponto)
        self.db.commit()
        self.db.refresh(db_ponto)
        return db_ponto
    
    def get_by_id(self, ponto_id: int) -> Optional[PontoTuristico]:
        """Buscar ponto turístico por ID"""
        return self.db.query(PontoTuristico).filter(PontoTuristico.id == ponto_id).first()
    
    def get_by_cidade(self, cidade_id: int) -> List[PontoTuristico]:
        """Buscar pontos turísticos por cidade"""
        return self.db.query(PontoTuristico).filter(PontoTuristico.cidade_id == cidade_id).all()
    
    def get_proximos(self, latitude: float, longitude: float, raio_km: float = 20) -> List[PontoTuristico]:
        """Buscar pontos turísticos próximos a uma coordenada"""
        delta = raio_km / 111.0
        
        return self.db.query(PontoTuristico).filter(
            PontoTuristico.latitude.between(latitude - delta, latitude + delta),
            PontoTuristico.longitude.between(longitude - delta, longitude + delta)
        ).all()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[PontoTuristico]:
        """Listar pontos turísticos com paginação"""
        return self.db.query(PontoTuristico).offset(skip).limit(limit).all()