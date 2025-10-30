#!/usr/bin/env python3
"""
Comando para popular banco de dados com cidades do IBGE
Uso: python populate_cities.py [UF]

Exemplos:
  python populate_cities.py          # Todas as cidades do Brasil
  python populate_cities.py SP       # Apenas São Paulo
  python populate_cities.py RJ       # Apenas Rio de Janeiro
"""

import asyncio
import sys
import os
from datetime import datetime

# Adicionar o diretório pai ao path para imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.services.ibge_service import IBGEService

def create_db_session():
    """Criar sessão do banco de dados"""
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

async def popular_cidades_comando(uf=None):
    """Função principal para popular cidades"""
    
    print("🚀 POPULADOR DE CIDADES IBGE")
    print("=" * 50)
    print(f"📅 Início: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Criar sessão do banco
    db = create_db_session()
    ibge_service = IBGEService(db)
    
    try:
        if uf:
            # Popular apenas uma UF específica
            print(f"🎯 Populando apenas a UF: {uf.upper()}")
            resultado = await ibge_service.popular_cidades_por_uf(uf.upper())
            
            print("\n📊 RESULTADO:")
            print(f"   UF: {resultado['uf']}")
            print(f"   Cidades inseridas: {resultado['cidades_inseridas']}")
            print(f"   Cidades atualizadas: {resultado['cidades_atualizadas']}")
            print(f"   Total processadas: {resultado['total']}")
            
        else:
            # Popular todas as cidades do Brasil
            print("🌎 Populando TODAS as cidades do Brasil...")
            print("⚠️  Este processo pode demorar alguns minutos...")
            
            resultado = await ibge_service.popular_todas_cidades()
            
            print("\n📊 RESULTADO FINAL:")
            print(f"   Estados processados: {resultado['estados_processados']}")
            print(f"   Total inseridas: {resultado['total_cidades_inseridas']}")
            print(f"   Total atualizadas: {resultado['total_cidades_atualizadas']}")
            print(f"   Total geral: {resultado['total_cidades_inseridas'] + resultado['total_cidades_atualizadas']}")
            
            print("\n📋 DETALHES POR ESTADO:")
            for detalhe in resultado['detalhes']:
                print(f"   {detalhe['uf']}: {detalhe['total']} cidades")
    
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        return False
    
    finally:
        db.close()
        print(f"\n🏁 Finalizado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    return True

def main():
    """Função principal do comando"""
    
    # Verificar argumentos
    uf = None
    if len(sys.argv) > 1:
        uf = sys.argv[1]
        
        # Validar UF
        ufs_validas = [
            'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 
            'MA', 'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 
            'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
        ]
        
        if uf.upper() not in ufs_validas:
            print(f"❌ UF inválida: {uf}")
            print(f"UFs válidas: {', '.join(ufs_validas)}")
            sys.exit(1)
    
    # Executar o processo
    sucesso = asyncio.run(popular_cidades_comando(uf))
    
    if sucesso:
        print("✅ Processo concluído com sucesso!")
        print("\n💡 Dicas:")
        print("   • Use a API para ver as cidades: GET /api/v1/cities/")
        print("   • Acesse a documentação: http://localhost:8000/docs")
    else:
        print("❌ Processo falhou!")
        sys.exit(1)

if __name__ == "__main__":
    main()