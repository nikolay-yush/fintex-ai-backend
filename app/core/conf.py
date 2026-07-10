import os
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


# --- APP MAIN SETTINGS ---
class AppSettings(BaseModel):
    VERSION: str = "0.1.0"
    PROJECT_NAME: str = "FintexAI"
    DESCRIPTION: str = "FintexAI is a platform to analyze financial data."
    DEBUG: bool = False
    PORT: int = 8000


# --- DB SETTINGS ---
class DBSettings(BaseModel):
    DB_HOST: str
    DB_PORT: int = 5432
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    @property
    def DB_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


class Settings(BaseSettings):
    app: AppSettings
    db: DBSettings

    model_config = SettingsConfigDict(
        env_file=f".env.{os.getenv('ENV_STATE', 'dev')}",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore"
    )

settings = Settings()  # type: ignore