"""
Централизованная конфигурация приложения.

Все настройки читаются из переменных окружения (или файла .env), чтобы
конфиденциальные данные никогда не были захардкожены в коде (DO-04).
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения, загружаемые из переменных окружения / .env файла."""

    # Безопасность
    secret_key: str = "dev-only-insecure-secret-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # База данных
    database_url: str = "sqlite:///./test.db"

    # Elasticsearch
    elasticsearch_url: str = "http://localhost:9200"

    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    search_cache_ttl_seconds: int = 300

    # Загрузка документов
    max_upload_size_mb: int = 20
    chunk_size: int = 1000
    chunk_overlap: int = 100

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()