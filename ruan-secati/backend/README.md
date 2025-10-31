# Backend - Comparador de Produtos com IA

API FastAPI para comparação de produtos utilizando IA Generativa (Google Gemini) com sistema de autenticação JWT e histórico de comparações.

## 🚀 Funcionalidades

- **Autenticação de usuários** com JWT
- **Comparação de produtos** usando IA Generativa (Google Gemini)
- **Histórico de comparações** por usuário
- **Banco de dados SQLite** para persistência
- **API RESTful** com documentação automática

## 📋 Pré-requisitos

- Python 3.8+
- Google API Key para Gemini
- Pip (gerenciador de pacotes Python)

## 🛠️ Instalação e Configuração

### 1. Crie um ambiente virtual
```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# No Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# No Windows (CMD)
venv\Scripts\activate

# No Linux/Mac
source venv/bin/activate
```

### 2. Instale as dependências
```bash
# Opção 1: Usando requirements.txt (recomendado)
pip install -r requirements.txt

### 3. Configure as variáveis de ambiente

Crie um arquivo `.env` na raiz do backend usando o template:

```bash
# Copie o arquivo de exemplo
cp .env.example .env
```

Edite o arquivo `.env` e adicione suas configurações:

```bash
# Arquivo .env
GEMINI_API_KEY=sua_chave_do_gemini_aqui
SECRET_KEY=sua_chave_secreta_jwt_super_segura_aqui
```

**Como obter a chave do Gemini:**
1. Acesse [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Faça login com sua conta Google
3. Clique em "Create API Key"
4. Copie a chave gerada

### 4. Inicialize o banco de dados
```bash
python create_db.py
```

## ▶️ Como Executar

### Desenvolvimento
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Produção
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

A API estará disponível em: `http://localhost:8000`

## 📚 Documentação da API

Após iniciar o servidor, acesse:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🔗 Endpoints Principais

### Autenticação
- `POST /user/create` - Criar novo usuário
- `POST /user/login` - Fazer login (retorna JWT token)
- `GET /users` - Listar todos os usuários

### Comparação de Produtos
- `POST /compare` - Comparar dois produtos (requer autenticação)
- `GET /history` - Histórico de comparações do usuário logado
- `GET /all_history` - Histórico de todas as comparações (admin)

## 📝 Exemplo de Uso

### 1. Criar usuário
```bash
curl -X POST "http://localhost:8000/user/create" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "meuusuario",
    "password": "minhasenha123"
  }'
```

### 2. Fazer login
```bash
curl -X POST "http://localhost:8000/user/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "meuusuario",
    "password": "minhasenha123"
  }'
```

### 3. Comparar produtos (com token)
```bash
curl -X POST "http://localhost:8000/compare" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SEU_TOKEN_AQUI" \
  -d '{
    "product1": "iPhone 15",
    "product2": "Samsung Galaxy S24"
  }'
```

## 🗄️ Estrutura do Banco de Dados

### Tabela Users
- `id` - Chave primária
- `username` - Nome de usuário (único)
- `hashed_password` - Senha hasheada
- `created_at` - Data de criação
- `updated_at` - Data de atualização

### Tabela History
- `id` - Chave primária
- `user_id` - ID do usuário
- `product1` - Nome do primeiro produto
- `product2` - Nome do segundo produto
- `comparison_result` - Resultado da comparação (JSON)
- `created_at` - Data de criação
- `updated_at` - Data de atualização

## 🔧 Configurações

### Variáveis de Ambiente
- `GEMINI_API_KEY` - Chave da API do Google Gemini (obrigatório)
- `SECRET_KEY` - Chave secreta para JWT (obrigatório)

### Configurações JWT
- **Algoritmo**: HS256
- **Tempo de expiração**: 30 minutos
- **Tipo de token**: Bearer

## 🚨 Solução de Problemas

### Erro "GEMINI_API_KEY not found"
- Verifique se o arquivo `.env` foi criado
- Confirme se a chave da API está correta
- Reinicie o servidor após adicionar a variável

### Erro de autenticação
- Verifique se o token JWT está sendo enviado no header
- Confirme se o token não expirou (30 minutos)
- Use o formato: `Authorization: Bearer seu_token_aqui`

### Erro de banco de dados
- Execute novamente: `python create_db.py`
- Verifique as permissões da pasta
- Delete o arquivo `app.db` e recrie se necessário

## 📂 Estrutura de Arquivos

```
backend/
├── main.py              # Aplicação principal FastAPI
├── models.py            # Modelos do banco de dados
├── schemas.py           # Esquemas Pydantic
├── database.py          # Configuração do banco
├── auth.py              # Sistema de autenticação
├── create_db.py         # Script para criar tabelas
├── requirements.txt     # Dependências do projeto
├── .env.example         # Exemplo de variáveis de ambiente
├── README.md            # Este arquivo
├── .env                 # Variáveis de ambiente (criar)
└── app.db               # Banco SQLite (gerado automaticamente)
```

## 🤝 Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.
