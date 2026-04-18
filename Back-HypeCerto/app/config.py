"""
config.py
Configurações centralizadas via pydantic-settings.
Lê variáveis do arquivo .env automaticamente.
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Banco de dados
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/hypecerto"

    # JWT
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 dias

    # Meta API
    USE_MOCK_META_API: bool = True
    META_APP_ID: str = ""
    META_APP_SECRET: str = ""
    META_API_VERSION: str = "v18.0"

    # OpenAI
    OPENAI_API_KEY: str = ""

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # Ambiente
    ENVIRONMENT: str = "development"

    @property
    def allowed_origins_list(self) -> List[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
