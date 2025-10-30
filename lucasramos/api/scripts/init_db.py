#!/usr/bin/env python3
"""
Script para inicializar o banco de dados usando o sistema de migrações
"""
import os
import sys
import subprocess
from pathlib import Path

def init_database():
    """Inicializar banco de dados executando todas as migrações"""
    print("🚀 INICIALIZANDO BANCO DE DADOS")
    print("=" * 50)
    
    # Caminho para o script de migração
    migrations_dir = Path(__file__).parent / "migrations"
    migrate_script = migrations_dir / "migrate.py"
    
    if not migrate_script.exists():
        print("❌ Script de migração não encontrado!")
        print(f"   Procurando em: {migrate_script}")
        return False
    
    try:
        print("📊 Verificando status das migrações...")
        
        # Executar status das migrações
        result = subprocess.run([
            sys.executable, str(migrate_script), "status"
        ], capture_output=True, text=True, cwd=str(Path(__file__).parent))
        
        if result.returncode != 0:
            print("⚠️ Erro ao verificar status das migrações:")
            print(result.stderr)
        else:
            print(result.stdout)
        
        print("\n🔄 Aplicando migrações pendentes...")
        
        # Executar migrações
        result = subprocess.run([
            sys.executable, str(migrate_script), "up"
        ], cwd=str(Path(__file__).parent))
        
        if result.returncode == 0:
            print("\n✅ Banco de dados inicializado com sucesso!")
            print("\n💡 Próximos passos:")
            print("1. Popule as cidades: python populate_cities.py")
            print("2. Inicie a API: python main.py")
            return True
        else:
            print("\n❌ Erro ao aplicar migrações!")
            return False
            
    except Exception as e:
        print(f"❌ Erro durante inicialização: {e}")
        return False

def main():
    """Função principal"""
    print("🏗️ SETUP DO BANCO DE DADOS")
    print("=" * 50)
    print("Este script irá:")
    print("• Executar todas as migrações pendentes")
    print("• Criar as tabelas necessárias")
    print("• Preparar o banco para uso")
    print("=" * 50)
    
    if init_database():
        print("\n🎉 Setup concluído com sucesso!")
        print("Seu banco de dados está pronto para uso!")
    else:
        print("\n💥 Falha no setup do banco!")
        sys.exit(1)

if __name__ == "__main__":
    main()