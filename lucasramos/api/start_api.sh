#!/bin/bash

echo "🚀 Iniciando Turismo Inteligente API"
echo "======================================"

# Verificar se o Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 não encontrado. Instale o Python 3.8+ primeiro."
    exit 1
fi

# Verificar se o pip está instalado
if ! command -v pip &> /dev/null && ! command -v pip3 &> /dev/null; then
    echo "❌ pip não encontrado. Instale o pip primeiro."
    exit 1
fi

# Usar pip3 se disponível, senão usar pip
PIP_CMD="pip"
if command -v pip3 &> /dev/null; then
    PIP_CMD="pip3"
fi

# Instalar dependências se necessário
echo "📦 Verificando dependências..."
if [ ! -d "venv" ]; then
    echo "🔧 Criando ambiente virtual..."
    python3 -m venv venv
fi

echo "🔄 Ativando ambiente virtual..."
source venv/bin/activate

echo "📥 Instalando/atualizando dependências..."
$PIP_CMD install -r requirements.txt

# Verificar se o banco está rodando
echo "🗃️ Verificando conexão com banco de dados..."
if ! nc -z localhost 5432; then
    echo "⚠️ Banco PostgreSQL não detectado na porta 5432"
    echo "▶️ Iniciando banco via Docker..."
    docker compose -f docker-compose.db.yml up -d
    echo "⏳ Aguardando banco inicializar..."
    sleep 5
fi

# Criar tabelas se necessário
echo "🏗️ Criando/verificando estrutura do banco..."
python init_db.py

echo "✅ Tudo pronto!"
echo ""
echo "🌐 Iniciando API na porta 8000..."
echo "📚 Documentação: http://localhost:8000/docs"
echo "❤️ Health check: http://localhost:8000/health"
echo ""
echo "Para parar a API: Ctrl+C"
echo "Para parar o banco: docker compose -f docker-compose.db.yml down"
echo ""

# Iniciar a API
uvicorn main:app --reload --host 0.0.0.0 --port 8000