# owner:POP MIRCEA STEFAN
# CRATE_DATE: 2024-06-20 10:40
# LAST MODIFY_DATE: --
# MODIFY BY: --

from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, field_validator
from pathlib import Path
from typing import List


class Settings(BaseSettings):
    # App
    APP_NAME: str = "TechFest Api"
    ENVIRONMENT: str = "dev"
    API_V1_PREFIX: str = "/api"

    # Oracle (Thin mode)
    ORACLE_USER: str
    ORACLE_PASSWORD: str
    ORACLE_HOST: str = "localhost"
    ORACLE_PORT: int = 1521
    ORACLE_SERVICE: str = "xepdb1"

    # CORS
    CORS_ORIGINS: List[AnyHttpUrl] | List[str] = []

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def split_origins(cls, v):
        if isinstance(v, str):
            return [o.strip() for o in v.split(",") if o.strip()]
        return v

    # SQLAlchemy URL pentru Oracle (driverul thin oracledb)
    def oracle_url(self) -> str:
        return (
            f"oracle+oracledb://{self.ORACLE_USER}:{self.ORACLE_PASSWORD}"
            f"@{self.ORACLE_HOST}:{self.ORACLE_PORT}/?service_name={self.ORACLE_SERVICE}"
        )


# Încarcă din .env (plasat în rădăcina proiectului)
_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
settings = Settings(_env_file=str(_ENV_PATH), _env_file_encoding="utf-8")
