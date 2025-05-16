import secrets

from pathlib import Path
from typing import List, Set
from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    BOT_TOKEN: str
    ORIGIN: str

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_SERVER: str
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str

    @computed_field
    @property
    def POSTGRESQL_DATABASE_URI(self) -> str:
        return (
            f"asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 180
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    UPLOAD_DIR: str = "uploads"

    ALLOWED_IMAGE_TYPES: List[str] = [
        "image/jpeg",
        "image/png",
        "image/gif",
        "image/webp",
    ]
    ALLOWED_IMAGE_EXTENSIONS: Set[str] = {
        "jpg",
        "jpeg",
        "png",
        "gif",
        "webp",
    }  # type: ignore
    MAX_IMAGE_SIZE: int = 10 * 1024 * 1024  # 10 MB


settings = Settings()

DATABASE_CONFIG = {
    "connections": {"default": settings.POSTGRESQL_DATABASE_URI},
    "apps": {
        "models": {
            "models": ["app.models.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}
