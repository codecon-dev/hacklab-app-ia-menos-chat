# 🌍 Turismo Inteligente API

Uma API desenvolvida em FastAPI para sugestões inteligentes de pontos turísticos em rotas entre cidades brasileiras, utilizando dados do IBGE e inteligência artificial.

## 🚀 Quick Start

**Instalação rápida e automática:**

```bash
cd api
./setup.sh
```

Este script irá configurar automaticamente:
- ✅ Ambiente virtual Python
- ✅ Dependências
- ✅ Banco de dados PostgreSQL
- ✅ Migrações
- ✅ Dados iniciais

## 📋 Funcionalidades

- **🏙️ Gerenciamento de Cidades**: CRUD completo para cidades brasileiras
- **🕷️ Crawler IBGE**: Popula automaticamente o banco com dados oficiais dos municípios
- **🗺️ Cálculo de Rotas**: Calcula distâncias e tempos de viagem entre cidades
- **🎯 Pontos Turísticos**: Encontra pontos turísticos na rota e proximidades
- **🤖 IA Integrada**: Gera sugestões personalizadas usando Gemini AI
- **👤 Sistema de Usuários**: Autenticação e gerenciamento de usuários
- **📚 Roteiros Salvos**: Salvar e compartilhar roteiros personalizados
- **🏗️ Arquitetura em Camadas**: Separação clara entre models, repositories, services e routes
- **🐳 Docker**: Containerização completa com PostgreSQL

## 🏗️ Arquitetura

```
api/
├── 📁 app/                    # Código principal da aplicação
│   ├── core/                  # Configurações e database
│   ├── models/                # Modelos SQLAlchemy (ORM)
│   ├── schemas/               # Esquemas Pydantic (validação)
│   ├── repositories/          # Camada de acesso a dados
│   ├── services/              # Lógica de negócio
│   └── routes/                # Endpoints da API
├── 📁 migrations/             # Sistema de migrações do banco
│   ├── migrate.py             # Gerenciador de migrações
│   ├── 001_initial_tables.py  # Migração inicial
│   ├── 002_create_users_table.py
│   └── 003_create_roteiros_table.py
├── 🐳 docker-compose.yml      # Orquestração Docker
├── 🐳 Dockerfile              # Container da aplicação
├── 📝 requirements.txt        # Dependências Python
├── ⚙️ .env.example            # Variáveis de ambiente exemplo
├── 🚀 setup.sh                # Script de instalação automática
├── 🔧 start_api.sh            # Script para iniciar API
├── 🗄️ db.sh                   # Scripts de gerenciamento do banco
├── 🏗️ init_db.py              # Inicialização do banco
└── 📖 README.md               # Esta documentação
```

## 🛠️ Tecnologias

- **🐍 FastAPI**: Framework web moderno e rápido para Python
- **🗃️ SQLAlchemy**: ORM para Python
- **🐘 PostgreSQL**: Banco de dados relacional robusto
- **🐳 Docker**: Containerização para desenvolvimento e produção
- **✅ Pydantic**: Validação de dados e serialização
- **🌐 httpx**: Cliente HTTP assíncrono
- **🤖 Google Gemini**: IA para geração de sugestões turísticas
- **🔐 JWT**: Autenticação segura com tokens
- **📊 Alembic**: Sistema de migrações de banco de dados

## 📦 Instalação e Execução

### 🎯 Método Recomendado: Setup Automático

```bash
# 1. Clone o repositório e acesse a pasta da API
cd api

# 2. Execute o setup automático
./setup.sh
```

O script de setup irá:
- ✅ Verificar dependências do sistema
- ✅ Criar ambiente virtual Python
- ✅ Instalar todas as dependências
- ✅ Configurar arquivo .env
- ✅ Iniciar PostgreSQL via Docker
- ✅ Executar todas as migrações
- ✅ Opcionalmente popular dados de cidades

### 🚀 Iniciar a Aplicação

```bash
# Opção 1: Script automatizado (recomendado)
./start_api.sh

# Opção 2: Manual
source venv/bin/activate
python main.py
```

### 🗄️ Gerenciamento do Banco de Dados

```bash
./db.sh start    # Iniciar PostgreSQL
./db.sh stop     # Parar PostgreSQL
./db.sh logs     # Ver logs do banco
./db.sh shell    # Conectar ao banco via psql
./db.sh status   # Ver status dos containers
./db.sh reset    # Resetar banco (cuidado!)
```

### 🔄 Sistema de Migrações

```bash
# Ver status das migrações
python migrations/migrate.py status

# Aplicar migrações pendentes
python migrations/migrate.py up

# Reverter última migração
python migrations/migrate.py down

# Reverter múltiplas migrações
python migrations/migrate.py down 2
```

## 🔧 Configuração

### Variáveis de Ambiente

Configure o arquivo `.env` baseado no `.env.example`:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/turismo_db

# API
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True

# Gemini AI (Opcional)
GEMINI_API_KEY=your_gemini_api_key_here

# JWT Authentication  
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## 🌎 Populando Dados

### Popular Cidades

```bash
# Popular todas as cidades do Brasil (demora ~30min)
python populate_cities.py

# Popular apenas uma UF específica
python populate_cities.py --uf SP
python populate_cities.py --uf RJ

# Popular múltiplas UFs
python populate_cities.py --uf SP,RJ,MG
```

## 📚 Uso da API

A API estará disponível em `http://localhost:8000`

- **📖 Documentação Interativa**: `http://localhost:8000/docs`
- **📋 OpenAPI Schema**: `http://localhost:8000/redoc`
- **❤️ Health Check**: `http://localhost:8000/health`

### 🔐 Autenticação

1. **Registrar usuário**:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@email.com",
    "senha": "minhasenha123"
  }'
```

2. **Fazer login**:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@email.com", 
    "senha": "minhasenha123"
  }'
```

### 🏙️ Consultar Cidades

```bash
# Listar cidades
curl "http://localhost:8000/api/v1/cities/?limit=10"

# Buscar cidade específica
curl "http://localhost:8000/api/v1/cities/buscar/São Paulo?uf=SP"
```

### 🗺️ Calcular Rota Turística

```bash
curl -X POST "http://localhost:8000/api/v1/tourism/rota" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SEU_TOKEN_AQUI" \
  -d '{
    "cidade_origem": "São Paulo",
    "cidade_destino": "Rio de Janeiro",
    "uf_origem": "SP",
    "uf_destino": "RJ",
    "preferencias": ["praias", "museus", "gastronomia"]
  }'
```

### 🎯 Buscar Pontos Turísticos Próximos

```bash
curl "http://localhost:8000/api/v1/tourism/pontos-proximos?latitude=-23.5505&longitude=-46.6333&raio_km=30" \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

### 📚 Gerenciar Roteiros Salvos

```bash
# Salvar roteiro
curl -X POST "http://localhost:8000/api/v1/roteiros/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SEU_TOKEN_AQUI" \
  -d '{
    "titulo": "Minha Viagem SP-RJ",
    "origem": "São Paulo, SP",
    "destino": "Rio de Janeiro, RJ",
    "conteudo": "Roteiro detalhado..."
  }'

# Listar meus roteiros
curl "http://localhost:8000/api/v1/roteiros/" \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

## 📡 Endpoints Principais

### 🔐 Autenticação (`/api/v1/auth`)
- `POST /register` - Registrar novo usuário  
- `POST /login` - Fazer login e obter token
- `GET /me` - Obter dados do usuário atual
- `PUT /me` - Atualizar perfil do usuário

### 🏙️ Cidades (`/api/v1/cities`)
- `GET /` - Listar cidades
- `GET /{cidade_id}` - Obter cidade por ID
- `GET /buscar/{nome}` - Buscar cidade por nome
- `POST /` - Criar nova cidade
- `PUT /{cidade_id}` - Atualizar cidade
- `DELETE /{cidade_id}` - Deletar cidade
- `POST /crawler/uf/{uf}` - Executar crawler para UF
- `POST /crawler/todos` - Executar crawler completo

### 🗺️ Turismo (`/api/v1/tourism`)
- `POST /rota` - Calcular rota turística
- `GET /pontos-proximos` - Buscar pontos próximos
- `GET /sugestoes-ia` - Obter sugestões da IA
- `GET /estatisticas` - Estatísticas do sistema

### 📚 Roteiros (`/api/v1/roteiros`)
- `GET /` - Listar meus roteiros
- `POST /` - Salvar novo roteiro
- `GET /{roteiro_id}` - Obter roteiro específico
- `PUT /{roteiro_id}` - Atualizar roteiro
- `DELETE /{roteiro_id}` - Deletar roteiro

## 🤖 Integração com IA

A API utiliza Google Gemini para gerar sugestões personalizadas:

1. **Configure a chave da API** no arquivo `.env`:
   ```env
   GEMINI_API_KEY=sua_chave_do_gemini_aqui
   ```

2. **Sem Gemini**: O sistema funciona normalmente com sugestões locais

3. **Obter chave gratuita**: [Google AI Studio](https://makersuite.google.com/app/apikey)

## 🐳 Desenvolvimento com Docker

### Executar toda aplicação com Docker

```bash
# Iniciar todos os serviços
docker-compose up --build

# Apenas banco de dados
docker-compose up -d db

# Ver logs
docker-compose logs -f

# Parar todos os serviços
docker-compose down
```

### 🔧 Scripts Úteis

```bash
# Gerenciamento do banco
./db.sh start|stop|logs|shell|status|reset

# Migrações
python migrations/migrate.py up|down|status

# Popular dados
python populate_cities.py [--uf SP]

# Iniciar API
./start_api.sh

# Setup completo
./setup.sh
```

## 🔍 Exemplo de Resposta

### Rota Turística com IA
```json
{
  "cidade_origem": {
    "id": 1,
    "nome": "São Paulo",
    "uf": "SP",
    "latitude": -23.5505,
    "longitude": -46.6333
  },
  "cidade_destino": {
    "id": 2,
    "nome": "Rio de Janeiro", 
    "uf": "RJ",
    "latitude": -22.9068,
    "longitude": -43.1729
  },
  "distancia_km": 357.42,
  "tempo_estimado_viagem": "4h 28min",
  "pontos_turisticos_rota": [
    {
      "nome": "Vale do Paraíba",
      "descricao": "Região histórica entre SP e RJ",
      "latitude": -23.2,
      "longitude": -45.5,
      "categoria": "histórico"
    }
  ],
  "sugestoes_ia": "🗺️ ROTEIRO TURÍSTICO: São Paulo/SP → Rio de Janeiro/RJ\n\n📍 PONTOS DE PARADA RECOMENDADOS:\n1. Aparecida do Norte - Santuário Nacional\n2. Campos do Jordão - Clima de montanha\n3. Paraty - Centro histórico colonial\n\n🍽️ GASTRONOMIA LOCAL:\n- Pastéis de Aparecida\n- Fondue em Campos do Jordão\n- Peixe com banana em Paraty\n\n⏰ TEMPO ESTIMADO: 2-3 dias com paradas turísticas"
}
```

## 📈 Monitoramento e Logs

- **Logs**: Exibidos no console durante execução
- **Health Check**: `/health` endpoint para verificar status
- **Estatísticas**: `/api/v1/tourism/estatisticas` para métricas do sistema
- **Métricas do Banco**: `./db.sh status` para status dos containers

## 🚧 Roadmap

### 🎯 Próximas Funcionalidades
- [ ] 🗺️ Integração com mapas interativos
- [ ] ⭐ Sistema de avaliações de pontos turísticos  
- [ ] 🔔 Notificações push para usuários
- [ ] 🌤️ Integração com API de clima
- [ ] 🚗 Otimização de rotas com algoritmos avançados
- [ ] 📱 App mobile React Native
- [ ] 🏪 Marketplace de guias turísticos locais
- [ ] 🎫 Integração com booking de hotéis/passagens

### 🔧 Melhorias Técnicas
- [ ] ⚡ Implementar cache Redis
- [ ] 📊 Logging estruturado com ELK Stack
- [ ] 🔍 Busca full-text com Elasticsearch
- [ ] 🚀 Deploy automatizado com CI/CD
- [ ] 📸 Upload de imagens de pontos turísticos
- [ ] 🔐 OAuth2 com Google/Facebook

## 🤝 Contribuição

1. 🍴 Faça um fork do projeto
2. 🌿 Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. ✅ Commit suas mudanças (`git commit -m 'Add: nova funcionalidade'`)
4. 📤 Push para a branch (`git push origin feature/nova-funcionalidade`)
5. 🔄 Abra um Pull Request

### � Padrões de Desenvolvimento
- **Commits**: Use [Conventional Commits](https://www.conventionalcommits.org/)
- **Code Style**: Siga PEP 8 para Python
- **Tests**: Adicione testes para novas funcionalidades
- **Docs**: Mantenha a documentação atualizada

## 🐛 Troubleshooting

### Problemas Comuns

**🔌 Erro de conexão com banco:**
```bash
# Verificar se PostgreSQL está rodando
./db.sh status

# Reiniciar banco
./db.sh stop && ./db.sh start
```

**📦 Erro nas migrações:**
```bash
# Ver status das migrações
python migrations/migrate.py status

# Reverter e aplicar novamente
python migrations/migrate.py down
python migrations/migrate.py up
```

**🐍 Problemas com ambiente Python:**
```bash
# Recriar ambiente virtual
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**🔑 Erro de autenticação Gemini:**
- Verifique se `GEMINI_API_KEY` está configurada no `.env`
- Teste a chave em: [Google AI Studio](https://makersuite.google.com/)

## 📞 Suporte

- 🐛 **Issues**: [GitHub Issues](https://github.com/codecon-dev/hacklab-app-ia-menos-chat/issues)
- 💬 **Discussões**: [GitHub Discussions](https://github.com/codecon-dev/hacklab-app-ia-menos-chat/discussions)
- 📧 **Email**: Para dúvidas específicas

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

<div align="center">

**🌟 Desenvolvido com ❤️ usando FastAPI e Python**

[⬆️ Voltar ao topo](#-turismo-inteligente-api)

</div>