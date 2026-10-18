"""
config.py
Configurações centralizadas via pydantic-settings.
Lê variáveis do arquivo .env automaticamente.
"""
import logging
import secrets
from typing import List, Optional

from pydantic import model_validator
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)

_INSECURE_KEYS = {"", "dev-secret-key-change-in-production", "chave-secreta-super-segura", "changeme"}


class Settings(BaseSettings):
    # Banco de dados
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/hypecerto"

    # JWT — SEM valor padrão público. Em produção é obrigatório definir SECRET_KEY (>= 32 caracteres).
    SECRET_KEY: Optional[str] = None
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60  # antes: 7 dias

    # Meta API
    USE_MOCK_META_API: bool = True
    META_APP_ID: str = ""
    META_APP_SECRET: str = ""
    META_API_VERSION: str = "v18.0"

    # OpenAI
    OPENAI_API_KEY: str = ""

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
    # Regex opcional (ex.: Codespaces). Só é aplicado quando ENVIRONMENT == "development".
    ALLOWED_ORIGIN_REGEX: str = r"https://.*\.github\.dev"

    # Upload
    MAX_UPLOAD_MB: int = 25

    # Ambiente
    ENVIRONMENT: str = "development"

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() in ("production", "prod")

    @property
    def allowed_origins_list(self) -> List[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]

    @model_validator(mode="after")
    def _validate_secret(self):
        weak = (self.SECRET_KEY or "").strip() in _INSECURE_KEYS or len(self.SECRET_KEY or "") < 32
        if weak:
            if self.is_production:
                raise ValueError(
                    "SECRET_KEY ausente ou fraca. Defina SECRET_KEY com >= 32 caracteres aleatórios "
                    "(ex.: python -c 'import secrets; print(secrets.token_urlsafe(48))')."
                )
            # Desenvolvimento: chave aleatória por processo (tokens deixam de valer ao reiniciar).
            self.SECRET_KEY = secrets.token_urlsafe(48)
            logger.warning("SECRET_KEY não definida/fraca: usando chave aleatória temporária (apenas desenvolvimento).")
        return self

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
