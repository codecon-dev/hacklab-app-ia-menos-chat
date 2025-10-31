# Arquitetura do Projeto

Este documento descreve a arquitetura, a árvore de pastas e os pontos de integração principais do projeto "Sentimental Analysis".

## Diagrama simples de fluxo (request)

1. Cliente (Angular) envia credenciais para `POST /api/v1/token/` → recebe `access` e `refresh` token.
2. Cliente envia `POST /api/v1/analysis/` (JSON) com header `Authorization: Bearer <access>`.
3. Backend (`TextMessageAPIView`) valida o payload pelo serializer e extrai texto.
4. Backend chama o cliente `google.genai` (Gemini) usando `GEMINI_KEY` para gerar a resposta de sentimento.
5. Backend retorna `{ "message": "<texto gerado pelo modelo>" }` para o cliente.

## Estrutura detalhada do backend (`sentimental_analysis_api/`)

- `manage.py` — utilitários Django (migrations, runserver, createsuperuser).
- `db.sqlite3` — banco de dados local (dev).
- `requirements.txt` — dependências Python do projeto.
- `sentimental_analysis_api/` (pacote do Django):
  - `settings.py` — configurações do Django; é onde `GEMINI_KEY` é referenciada.
  - `urls.py` — rotas do projeto:
    - `/admin/` — admin Django
    - `/swagger/`, `/redoc/` — documentação (drf-yasg)
    - `/api/v1/token/` e `/api/v1/token/refresh/` — JWT (Simple JWT)
    - `/api/v1/analysis/` — `TextMessageAPIView` (análise de texto)
    - `/api/v1/analysis/document` — `FileMessageAPIView` (análise a partir de arquivo)
  - `asgi.py`, `wsgi.py` — pontos de entrada ASGI/WSGI.

- App `analysis/`:
  - `views/`:
    - `text_message_view.py` — `TextMessageAPIView` (POST: recebe JSON `{ message }`)
    - `file_message_view.py` — `FileMessageAPIView` (POST: recebe arquivo `file` em multipart/form-data)
  - `serializers/`:
    - `text_message_serializer.py` — valida `message` (CharField).
    - `file_message_serializer.py` — valida `file` (FileField).
  - `models.py` — modelos do banco (sem modelos persistidos).
  - `migrations/` — histórico de migrações.

## Estrutura detalhada do frontend (`sentimental_analysis_front/`)

- `package.json` / `package-lock.json` — dependências e scripts do Angular CLI.
- `angular.json` — configuração do workspace do Angular.
- `src/` — código-fonte:
  - `index.html` / `main.ts` — bootstrapping da aplicação.
  - `styles/` — estilos globais.
  - `app/` — núcleo da aplicação:
    - `app.ts`, `app.routes.ts`, `app.config.ts` — configuração e roteamento.
    - `components/` — componentes reutilizáveis (ex.: `default-login`, `primary-input`).
    - `pages/` — páginas da aplicação (ex.: `home-page`, `login`, `register`).
    - `services/` — serviços para chamadas HTTP (ex.: `login.service.ts`).
    - `guards/` — guards de rota (ex.: `auth.guard.ts`) que protegem rotas com base no JWT.
