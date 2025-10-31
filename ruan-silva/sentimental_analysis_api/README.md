# Sentimental Analysis API

Esta sessão contém o passo a passo de como executar o projeto localmente e mais informações sobre os endpoints.

## 🚀 Quick Start

1. Abra a API em sua máquina:

        cd sentimental_analysis_api

2. Crie uma máquina virtual:

        python -m venv venv

3. Ative a máquina virtual:

        venv/Scripts/activate

4. Instale as dependências:

        pip install -r requirements.txt

5. Crie um arquivo `.env` para as variáveis de ambiente dentro da pasta atual.

6. No arquivo `.env`, ensira as variáveis de ambiente:

		DJANGO_SECRET_KEY=<sua_secret_key_django>
		GEMINI_API_KEY=<sua_api_key_gemini>

7. Execute as migrações:

        python manage.py migrate

8. Inicie o servidor:

        python manage.py runserver

9. Acesse o Swagger para iniciar:

        http://127.0.0.1:8000/swagger/

## Arquitetura e endpoints importantes

- `POST /api/v1/token/` — obter tokens JWT (username e password).
- `POST /api/v1/token/refresh/` — renovar token.
- `POST /api/v1/analysis/` — analisar texto (JSON):
	- Payload: `{ "message": "texto a analisar" }`
	- Retorno: `{ "message": "<resposta gerada pelo modelo>" }`
	- Requer autenticação Bearer JWT.
- `POST /api/v1/analysis/document` — enviar arquivo (multipart/form-data) com campo `file` (TXT ou PDF):
	- Retorno: `{ "message": "<resposta gerada pelo modelo>" }`
	- Requer autenticação Bearer JWT.
- `GET /swagger/` e `GET /redoc/` — documentação automática (drf-yasg).
- `GET /admin/` — admin Django.

## Exemplos de uso

- Obter token (curl):

```bash
curl -X POST http://127.0.0.1:8000/api/v1/token/ -H "Content-Type: application/json" -d '{"username":"seu_usuario","password":"sua_senha"}'
```

- Analisar texto (curl):

```bash
curl -X POST http://127.0.0.1:8000/api/v1/analysis/ \
	-H "Authorization: Bearer <ACCESS_TOKEN>" \
	-H "Content-Type: application/json" \
	-d '{"message":"Estou muito feliz hoje"}'
```