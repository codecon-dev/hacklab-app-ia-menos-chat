"""
README das Migrações

Este diretório contém todas as migrações do banco de dados do projeto.
As migrações são executadas em ordem sequencial baseada no número da versão.
"""

# 📁 Estrutura das Migrações

## Arquivos
- `migrate.py` - Script principal para gerenciar migrações
- `001_initial_tables.py` - Criação das tabelas iniciais (cidades, pontos_turisticos)  
- `002_create_users_table.py` - Criação da tabela de usuários
- `003_create_roteiros_table.py` - Criação da tabela de roteiros salvos

## 🚀 Como usar

### Aplicar todas as migrações pendentes
```bash
python migrations/migrate.py up
```

### Verificar status das migrações
```bash
python migrations/migrate.py status
```

### Reverter a última migração
```bash
python migrations/migrate.py down
```

### Reverter as últimas 2 migrações
```bash
python migrations/migrate.py down 2
```

## 📝 Criando uma nova migração

1. Crie um novo arquivo seguindo o padrão: `00X_descricao_da_migracacao.py`
2. Implemente as funções `upgrade()` e `downgrade()`
3. Execute `python migrations/migrate.py up` para aplicar

### Exemplo de estrutura:
```python
"""
Migration 004: Add new feature

Created: 2024-10-30
Description: Description of what this migration does
"""

revision = '004'
down_revision = '003'

def upgrade():
    \"\"\"Apply the migration\"\"\"
    # Código para aplicar a migração
    pass

def downgrade():
    \"\"\"Rollback the migration\"\"\"
    # Código para reverter a migração
    pass
```

## 🔍 Tabela de Controle

O sistema mantém uma tabela `schema_migrations` que armazena:
- `version`: Número da versão da migração
- `applied_at`: Timestamp de quando foi aplicada
- `description`: Descrição da migração

## ⚠️ Importante

- **Nunca modifique migrações já aplicadas** em produção
- **Sempre teste migrações** em ambiente de desenvolvimento primeiro
- **Faça backup** do banco antes de aplicar migrações em produção
- **Execute migrações** em ordem sequencial