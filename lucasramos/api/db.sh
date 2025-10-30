#!/bin/bash

case "$1" in
    start)
        echo "🗃️ Iniciando PostgreSQL via Docker..."
        docker compose -f docker-compose.yml up -d
        echo "✅ PostgreSQL iniciado na porta 5432"
        echo "📊 Para verificar logs: ./db.sh logs"
        ;;
    stop)
        echo "⏹️ Parando PostgreSQL..."
        docker compose -f docker-compose.yml down
        echo "✅ PostgreSQL parado"
        ;;
    restart)
        echo "🔄 Reiniciando PostgreSQL..."
        docker compose -f docker-compose.yml restart
        echo "✅ PostgreSQL reiniciado"
        ;;
    logs)
        echo "📋 Logs do PostgreSQL:"
        docker compose -f docker-compose.yml logs -f
        ;;
    status)
        echo "📊 Status dos containers:"
        docker compose -f docker-compose.yml ps
        ;;
    shell)
        echo "🐘 Conectando ao PostgreSQL..."
        docker compose -f docker-compose.yml exec db psql -U user -d turismo_db
        ;;
    clean)
        echo "🧹 Removendo dados do PostgreSQL..."
        read -p "⚠️ Isso irá apagar todos os dados. Continuar? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker compose -f docker-compose.yml down -v
            echo "✅ Dados removidos"
        else
            echo "❌ Operação cancelada"
        fi
        ;;
    *)
        echo "🗃️ Gerenciador do PostgreSQL"
        echo "=========================="
        echo "Uso: ./db.sh [comando]"
        echo ""
        echo "Comandos disponíveis:"
        echo "  start   - Iniciar PostgreSQL"
        echo "  stop    - Parar PostgreSQL"
        echo "  restart - Reiniciar PostgreSQL"
        echo "  logs    - Ver logs"
        echo "  status  - Ver status"
        echo "  shell   - Conectar ao PostgreSQL"
        echo "  clean   - Remover todos os dados"
        echo ""
        echo "Exemplos:"
        echo "  ./db.sh start"
        echo "  ./db.sh logs"
        echo "  ./db.sh shell"
        ;;
esac