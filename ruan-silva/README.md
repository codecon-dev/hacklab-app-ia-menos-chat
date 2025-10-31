# Sentimental Analysis

Ferramenta de análise de sentimento que combina um backend em Django REST Framework e um frontend em Angular, utilizando a API GenAI (Gemini) para identificar emoções expressas em textos e fornecer explicações sobre.

## 🌟 Visão geral

- Backend: `sentimental_analysis_api/`
- Frontend: `sentimental_analysis_front/`
- Banco de dados: `sentimental_analysis_api/db.sqlite3` - *Gerado após executar o servidor pela primeira vez.*
- Modelo de IA: API do Gemini

## 📌 Funcionalidades atuais

- Login: Permite que o usuário acesse a aplicação e suas operações;
- Análise de texto: Permite o usuário enviar determinado texto e obter o retorno sobre o sentimento expressado pelo autor;
- Documentação da API: Integração com o Swagger para registro dos endpoints do sistema.

## ⭐ Funcionalidades futuras

- Register e LogOut: Permite ao usuário criar acesso ao sistema e encerrar login quando necessário;
- Arquivos de texto: Permite o usuário enviar arquivos `.txt` ou `.pdf` para análise do conteúdo.

## 📁 Estrutura do repositório

Você pode encontrar mais informações sobre a arquitetura da aplicação em [ARCHITECTURE.md](ARCHITECTURE.md).

## ⚙️ Setup do projeto

- Backend: acesse [sentimental_analysis_api/README.md](sentimental_analysis_api/README.md) para executar a API localmente.
- Frontend: acesse[sentimental_analysis_front/README.md](sentimental_analysis_front/README.md) para executar a UI localmente.

## ✒️ Autor

- **Ruan Carlos da Silva** - *Desenvolvedor FullStack* - [Github](https://github.com/ruansilva123)