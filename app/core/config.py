from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Pydantic автоматически поищет эти переменные в .env (регистр не важен)
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int

    DATABASE_URL: str

    # Настройки для самого Pydantic: указывать, откуда брать переменные
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


# Создаем синглтон (единственный экземпляр настроек) для импорта в другие модули
settings = Settings()