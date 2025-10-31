#!/usr/bin/env python3
"""
Script para criar as tabelas do banco de dados SQLite
"""

from database import engine, Base
from models import User, History

def create_tables():
    """Cria todas as tabelas definidas nos modelos"""
    print("Criando tabelas do banco de dados...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tabelas criadas com sucesso!")
    
    # Verificar se as tabelas foram criadas
    print("\nTabelas criadas:")
    print("- users")
    print("- history")

if __name__ == "__main__":
    create_tables()