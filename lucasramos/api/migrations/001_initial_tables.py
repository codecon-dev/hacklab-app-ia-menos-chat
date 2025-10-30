"""
Migration 001: Create initial tables (cidades and pontos_turisticos)

Created: 2024-10-04
Description: Creates the initial database schema with cities and tourist points tables
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    """Create initial tables"""
    print("🚀 Executando migração 001: Criando tabelas iniciais...")
    
    # Create cidades table
    print("📝 Criando tabela 'cidades'...")
    op.create_table('cidades',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(length=255), nullable=False),
        sa.Column('nome_normalizado', sa.String(length=255), nullable=False),
        sa.Column('uf', sa.String(length=2), nullable=False),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('ibge_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for cidades
    print("📊 Criando índices para 'cidades'...")
    op.create_index('ix_cidades_id', 'cidades', ['id'])
    op.create_index('ix_cidades_nome', 'cidades', ['nome'])
    op.create_index('ix_cidades_nome_normalizado', 'cidades', ['nome_normalizado'])
    op.create_index('ix_cidades_uf', 'cidades', ['uf'])
    op.create_index('ix_cidades_ibge_id', 'cidades', ['ibge_id'])
    
    # Create unique constraint for ibge_id
    op.create_unique_constraint('uq_cidades_ibge_id', 'cidades', ['ibge_id'])
    
    # Create pontos_turisticos table
    print("📝 Criando tabela 'pontos_turisticos'...")
    op.create_table('pontos_turisticos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(length=255), nullable=False),
        sa.Column('descricao', sa.Text(), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('cidade_id', sa.Integer(), nullable=True),
        sa.Column('categoria', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for pontos_turisticos
    print("📊 Criando índices para 'pontos_turisticos'...")
    op.create_index('ix_pontos_turisticos_id', 'pontos_turisticos', ['id'])
    op.create_index('ix_pontos_turisticos_cidade_id', 'pontos_turisticos', ['cidade_id'])
    op.create_index('ix_pontos_turisticos_categoria', 'pontos_turisticos', ['categoria'])
    
    print("✅ Migração 001 concluída com sucesso!")

def downgrade():
    """Drop tables"""
    print("⬇️ Revertendo migração 001...")
    op.drop_table('pontos_turisticos')
    op.drop_table('cidades')
    print("✅ Migração 001 revertida com sucesso!")