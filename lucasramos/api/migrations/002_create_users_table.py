"""
Migration 002: Create users table

Created: 2024-10-15
Description: Creates the users table for authentication system
"""

import sys
import os
from sqlalchemy import create_engine, text, Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None

def upgrade():
    """Create users table"""
    print("🚀 Executando migração 002: Criando tabela de usuários...")
    
    # Adicionar o diretório pai ao path para importar os módulos
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from app.core.config import settings
    from app.core.database import Base
    from app.models.usuario import Usuario
    
    try:
        # Criar engine
        engine = create_engine(settings.DATABASE_URL)
        
        print(f"📝 Conectando ao banco: {settings.DATABASE_URL}")
        
        # Criar todas as tabelas (incluindo a nova tabela de usuários)
        Base.metadata.create_all(bind=engine)
        
        print("✅ Tabela de usuários criada com sucesso!")
        
        # Verificar se a tabela foi criada
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'usuarios'
            """))
            
            if result.fetchone():
                print("✅ Tabela 'usuarios' confirmada no banco de dados")
                
                # Mostrar estrutura da tabela
                result = conn.execute(text("""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns 
                    WHERE table_name = 'usuarios'
                    ORDER BY ordinal_position
                """))
                
                print("\n📋 Estrutura da tabela 'usuarios':")
                print("-" * 60)
                for row in result:
                    nullable = "NULL" if row[2] == "YES" else "NOT NULL"
                    default = f" DEFAULT {row[3]}" if row[3] else ""
                    print(f"  {row[0]:<15} {row[1]:<15} {nullable}{default}")
                    
            else:
                print("❌ Erro: Tabela 'usuarios' não foi criada")
                raise Exception("Falha ao criar tabela de usuários")
                
    except Exception as e:
        print(f"❌ Erro ao criar tabela: {e}")
        raise e
    
    print("✅ Migração 002 concluída com sucesso!")

def downgrade():
    """Drop users table"""
    print("⬇️ Revertendo migração 002...")
    
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from app.core.config import settings
    
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS usuarios CASCADE"))
        conn.commit()
    
    print("✅ Migração 002 revertida com sucesso!")