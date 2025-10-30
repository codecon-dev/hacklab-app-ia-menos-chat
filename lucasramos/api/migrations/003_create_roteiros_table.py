"""
Migration 003: Create roteiros table

Created: 2024-10-20
Description: Creates the roteiros (travel itineraries) table for saving user routes
"""

import sys
import os
from sqlalchemy import create_engine, text

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None

def upgrade():
    """Create roteiros table"""
    print("🚀 Executando migração 003: Criando tabela de roteiros...")
    
    # Adicionar o diretório pai ao path para importar os módulos
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from app.core.config import settings
    
    # Criar engine
    engine = create_engine(settings.DATABASE_URL)
    
    try:
        # Criar tabela de roteiros
        print("📝 Criando tabela de roteiros...")
        
        # SQL para criar a tabela
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS roteiros (
            id SERIAL PRIMARY KEY,
            titulo VARCHAR(255) NOT NULL,
            origem VARCHAR(255) NOT NULL,
            destino VARCHAR(255) NOT NULL,
            preferencias TEXT,
            conteudo TEXT NOT NULL,
            pontos_json TEXT,
            usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        with engine.connect() as conn:
            conn.execute(text(create_table_sql))
            conn.commit()
            print("✅ Tabela 'roteiros' criada com sucesso!")
            
            # Criar índices
            print("📊 Criando índices...")
            indices_sql = [
                "CREATE INDEX IF NOT EXISTS idx_roteiros_usuario_id ON roteiros(usuario_id);",
                "CREATE INDEX IF NOT EXISTS idx_roteiros_data_criacao ON roteiros(data_criacao DESC);",
                "CREATE INDEX IF NOT EXISTS idx_roteiros_titulo ON roteiros(titulo);"
            ]
            
            for index_sql in indices_sql:
                conn.execute(text(index_sql))
                conn.commit()
            
            print("✅ Índices criados com sucesso!")
            
            # Verificar estrutura da tabela
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'roteiros'
                ORDER BY ordinal_position;
            """))
            
            print("\n📋 Estrutura da tabela 'roteiros':")
            for row in result:
                print(f"  - {row[0]}: {row[1]} ({'NULL' if row[2] == 'YES' else 'NOT NULL'})")
            
    except Exception as e:
        print(f"❌ Erro ao criar tabela: {e}")
        raise e
    
    print("✅ Migração 003 concluída com sucesso!")

def downgrade():
    """Drop roteiros table"""
    print("⬇️ Revertendo migração 003...")
    
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from app.core.config import settings
    
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS roteiros CASCADE"))
        conn.commit()
    
    print("✅ Migração 003 revertida com sucesso!")