#!/bin/bash

# ========================================
# 🚀 SETUP AUTOMÁTICO DO PROJETO
# ========================================

set -e  # Parar em caso de erro

echo "🏗️ SETUP DO BACKEND - TURISMO INTELIGENTE"
echo "=========================================="
echo ""

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para logs coloridos
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Verificar se está na pasta correta
if [ ! -f "main.py" ]; then
    log_error "Execute este script a partir da pasta 'api' do projeto"
    exit 1
fi

log_info "Verificando dependências do sistema..."

# Verificar Python
if ! command -v python3 &> /dev/null; then
    log_error "Python 3 não está instalado"
    exit 1
fi

# Verificar Docker
if ! command -v docker &> /dev/null; then
    log_error "Docker não está instalado"
    exit 1
fi

# Verificar Docker Compose
if ! command -v docker-compose &> /dev/null; then
    log_error "Docker Compose não está instalado"
    exit 1
fi

log_success "Dependências do sistema verificadas"

# 1. Configurar ambiente Python
log_info "Configurando ambiente Python..."

if [ ! -d "venv" ]; then
    log_info "Criando ambiente virtual..."
    python3 -m venv venv
fi

log_info "Ativando ambiente virtual..."
source venv/bin/activate

log_info "Instalando dependências Python..."
pip install --upgrade pip
pip install -r requirements.txt

log_success "Ambiente Python configurado"

# 2. Configurar arquivo .env
log_info "Configurando variáveis de ambiente..."

if [ ! -f ".env" ]; then
    log_info "Criando arquivo .env a partir do .env.example..."
    cp .env.example .env
    log_warning "Revise o arquivo .env para ajustar configurações se necessário"
else
    log_info "Arquivo .env já existe"
fi

log_success "Variáveis de ambiente configuradas"

# 3. Iniciar banco de dados PostgreSQL
log_info "Iniciando banco de dados PostgreSQL..."

# Parar containers existentes (se houver)
docker-compose down 2>/dev/null || true

# Iniciar apenas o serviço do banco
log_info "Subindo container PostgreSQL..."
docker-compose up -d db

# Aguardar banco ficar disponível
log_info "Aguardando banco de dados ficar disponível..."
sleep 10

# Verificar se o banco está rodando
if ! docker-compose ps | grep -q "Up"; then
    log_error "Falha ao iniciar banco de dados"
    exit 1
fi

log_success "Banco de dados PostgreSQL iniciado"

# 4. Executar migrações
log_info "Executando migrações do banco de dados..."

python init_db.py

log_success "Migrações executadas com sucesso"

# 5. Popular dados iniciais (opcional)
echo ""
read -p "🌎 Deseja popular o banco com dados das cidades brasileiras? (s/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Ss]$ ]]; then
    log_info "Populando banco com dados das cidades..."
    log_warning "Isso pode demorar alguns minutos..."
    
    # Popular apenas algumas UFs principais para começar
    python populate_cities.py --uf SP
    python populate_cities.py --uf RJ
    python populate_cities.py --uf MG
    
    log_success "Dados das principais cidades carregados"
    log_info "Para carregar mais cidades, execute: python populate_cities.py"
fi

# 6. Verificar se tudo está funcionando
log_info "Verificando configuração..."

# Testar conexão com banco
python -c "
from app.core.database import engine
from sqlalchemy import text
try:
    with engine.connect() as conn:
        result = conn.execute(text('SELECT COUNT(*) FROM cidades'))
        count = result.fetchone()[0]
        print(f'✅ Banco conectado! {count} cidades carregadas')
except Exception as e:
    print(f'❌ Erro na conexão: {e}')
    exit(1)
"

echo ""
echo "🎉 SETUP CONCLUÍDO COM SUCESSO!"
echo "================================"
echo ""
echo "📋 PRÓXIMOS PASSOS:"
echo ""
echo "1. 🚀 Iniciar a API:"
echo "   ./start_api.sh"
echo "   ou"
echo "   source venv/bin/activate && python main.py"
echo ""
echo "2. 🌐 Acessar a API:"
echo "   http://localhost:8000"
echo "   Documentação: http://localhost:8000/docs"
echo ""
echo "3. 🗄️ Gerenciar banco de dados:"
echo "   ./db.sh status    # Ver status"
echo "   ./db.sh logs      # Ver logs"
echo "   ./db.sh shell     # Conectar ao banco"
echo "   ./db.sh stop      # Parar banco"
echo ""
echo "4. 🔄 Gerenciar migrações:"
echo "   python migrations/migrate.py status  # Ver status"
echo "   python migrations/migrate.py up     # Aplicar pendentes"
echo ""
echo "5. 🌎 Popular mais cidades:"
echo "   python populate_cities.py           # Todas as cidades"
echo "   python populate_cities.py --uf RS   # Apenas RS"
echo ""
echo "💡 Para dúvidas, consulte o README.md"
echo ""