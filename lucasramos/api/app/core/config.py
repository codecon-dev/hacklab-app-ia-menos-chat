from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Configurações do Banco de Dados
    DATABASE_URL: str = "postgresql://user:password@db:5432/turismo_db"
    
    # Configurações da API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = True
    
    # Configurações da OpenAI
    OPENAI_API_KEY: Optional[str] = None
    
    # Configurações do Gemini
    GEMINI_API_KEY: Optional[str] = None
    
    # PostgreSQL
    POSTGRES_USER: str = "user"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "turismo_db"
    
    class Config:
        env_file = ".env"

settings = Settings()