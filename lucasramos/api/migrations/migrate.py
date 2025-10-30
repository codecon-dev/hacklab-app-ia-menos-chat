"""
Sistema de Migration Manager

Este script gerencia a execução das migrações do banco de dados de forma ordenada.
"""

import sys
import os
import importlib.util
from pathlib import Path
from sqlalchemy import create_engine, text
from typing import List, Dict

# Adicionar o diretório pai ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings

class MigrationManager:
    """Gerenciador de migrações do banco de dados"""
    
    def __init__(self):
        self.migrations_dir = Path(__file__).parent
        self.engine = create_engine(settings.DATABASE_URL)
        self._ensure_migration_table()
    
    def _ensure_migration_table(self):
        """Criar tabela de controle de migrações se não existir"""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version VARCHAR(10) PRIMARY KEY,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            description TEXT
        );
        """
        
        with self.engine.connect() as conn:
            conn.execute(text(create_table_sql))
            conn.commit()
    
    def get_applied_migrations(self) -> List[str]:
        """Obter lista de migrações já aplicadas"""
        with self.engine.connect() as conn:
            result = conn.execute(text(
                "SELECT version FROM schema_migrations ORDER BY version"
            ))
            return [row[0] for row in result]
    
    def get_available_migrations(self) -> List[Dict]:
        """Obter lista de migrações disponíveis"""
        migrations = []
        
        for file_path in sorted(self.migrations_dir.glob("*.py")):
            if file_path.name.startswith("__"):
                continue
                
            if file_path.name == "migrate.py":
                continue
            
            # Extrair número da migração do nome do arquivo
            parts = file_path.stem.split("_", 1)
            if len(parts) >= 2:
                version = parts[0]
                description = parts[1].replace("_", " ").title()
                
                migrations.append({
                    "version": version,
                    "description": description,
                    "file_path": file_path,
                    "module_name": file_path.stem
                })
        
        return migrations
    
    def load_migration_module(self, file_path: Path):
        """Carregar módulo de migração dinamicamente"""
        spec = importlib.util.spec_from_file_location("migration", file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    
    def apply_migration(self, migration: Dict):
        """Aplicar uma migração específica"""
        print(f"\n📦 Aplicando migração {migration['version']}: {migration['description']}")
        
        try:
            # Carregar e executar migração
            module = self.load_migration_module(migration['file_path'])
            
            if hasattr(module, 'upgrade'):
                module.upgrade()
                
                # Registrar migração como aplicada
                with self.engine.connect() as conn:
                    conn.execute(text("""
                        INSERT INTO schema_migrations (version, description) 
                        VALUES (:version, :description)
                        ON CONFLICT (version) DO NOTHING
                    """), {
                        "version": migration['version'],
                        "description": migration['description']
                    })
                    conn.commit()
                
                print(f"✅ Migração {migration['version']} aplicada com sucesso!")
                return True
            else:
                print(f"⚠️ Migração {migration['version']} não possui função 'upgrade'")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao aplicar migração {migration['version']}: {e}")
            return False
    
    def rollback_migration(self, migration: Dict):
        """Reverter uma migração específica"""
        print(f"\n🔄 Revertendo migração {migration['version']}: {migration['description']}")
        
        try:
            # Carregar e executar rollback
            module = self.load_migration_module(migration['file_path'])
            
            if hasattr(module, 'downgrade'):
                module.downgrade()
                
                # Remover registro da migração
                with self.engine.connect() as conn:
                    conn.execute(text(
                        "DELETE FROM schema_migrations WHERE version = :version"
                    ), {"version": migration['version']})
                    conn.commit()
                
                print(f"✅ Migração {migration['version']} revertida com sucesso!")
                return True
            else:
                print(f"⚠️ Migração {migration['version']} não possui função 'downgrade'")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao reverter migração {migration['version']}: {e}")
            return False
    
    def migrate_up(self):
        """Aplicar todas as migrações pendentes"""
        print("🚀 Iniciando processo de migração...")
        print("=" * 60)
        
        applied = self.get_applied_migrations()
        available = self.get_available_migrations()
        
        print(f"📊 Migrações aplicadas: {len(applied)}")
        print(f"📦 Migrações disponíveis: {len(available)}")
        
        # Filtrar migrações pendentes
        pending = [m for m in available if m['version'] not in applied]
        
        if not pending:
            print("\n✅ Todas as migrações estão em dia!")
            return
        
        print(f"\n🔄 Migrações pendentes: {len(pending)}")
        
        # Aplicar migrações pendentes
        success_count = 0
        for migration in pending:
            if self.apply_migration(migration):
                success_count += 1
            else:
                print(f"\n❌ Falha ao aplicar migração {migration['version']}. Parando...")
                break
        
        print("\n" + "=" * 60)
        print(f"✅ Processo concluído! {success_count}/{len(pending)} migrações aplicadas.")
    
    def migrate_down(self, steps: int = 1):
        """Reverter as últimas N migrações"""
        print(f"🔄 Revertendo as últimas {steps} migração(ões)...")
        print("=" * 60)
        
        applied = self.get_applied_migrations()
        available = self.get_available_migrations()
        
        if not applied:
            print("⚠️ Nenhuma migração para reverter!")
            return
        
        # Ordenar migrações aplicadas em ordem decrescente
        applied.reverse()
        
        # Reverter as últimas N migrações
        success_count = 0
        for i in range(min(steps, len(applied))):
            version = applied[i]
            migration = next((m for m in available if m['version'] == version), None)
            
            if migration:
                if self.rollback_migration(migration):
                    success_count += 1
                else:
                    print(f"\n❌ Falha ao reverter migração {version}. Parando...")
                    break
            else:
                print(f"⚠️ Arquivo de migração para versão {version} não encontrado!")
        
        print("\n" + "=" * 60)
        print(f"✅ Processo concluído! {success_count} migração(ões) revertida(s).")
    
    def status(self):
        """Mostrar status das migrações"""
        print("📊 STATUS DAS MIGRAÇÕES")
        print("=" * 60)
        
        applied = self.get_applied_migrations()
        available = self.get_available_migrations()
        
        print(f"🗄️ Banco de dados: {settings.DATABASE_URL}")
        print(f"📁 Pasta de migrações: {self.migrations_dir}")
        print(f"📦 Migrações disponíveis: {len(available)}")
        print(f"✅ Migrações aplicadas: {len(applied)}")
        
        print("\n📋 DETALHES DAS MIGRAÇÕES:")
        print("-" * 60)
        
        for migration in available:
            status = "✅ APLICADA" if migration['version'] in applied else "⏳ PENDENTE"
            print(f"{migration['version']:<5} | {status:<12} | {migration['description']}")
        
        pending = [m for m in available if m['version'] not in applied]
        if pending:
            print(f"\n⚠️ {len(pending)} migração(ões) pendente(s)")
        else:
            print("\n🎉 Todas as migrações estão em dia!")

def main():
    """Função principal"""
    if len(sys.argv) < 2:
        print("📋 USO:")
        print("  python migrate.py up           # Aplicar todas as migrações pendentes")
        print("  python migrate.py down [N]     # Reverter as últimas N migrações (padrão: 1)")
        print("  python migrate.py status       # Mostrar status das migrações")
        return
    
    manager = MigrationManager()
    command = sys.argv[1]
    
    if command == "up":
        manager.migrate_up()
    elif command == "down":
        steps = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        manager.migrate_down(steps)
    elif command == "status":
        manager.status()
    else:
        print(f"❌ Comando desconhecido: {command}")
        print("💡 Use: up, down ou status")

if __name__ == "__main__":
    main()