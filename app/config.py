from enum import Enum
from typing import Any

from dotenv import find_dotenv, load_dotenv
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv(find_dotenv(".env"))


class Environment(str, Enum):
    """Класс с константами окружения приложения"""

    LOCAL = "LOCAL"
    STAGING = "STAGING"
    TESTING = "TESTING"
    PRODUCTION = "PRODUCTION"

    @property
    def is_debug(self):
        """Проверяет, является ли окружение отладочным."""
        return self in (self.LOCAL, self.STAGING, self.TESTING)

    @property
    def is_testing(self):
        """Проверяет, является ли окружение тестовым."""
        return self == self.TESTING

    @property
    def is_deployed(self) -> bool:
        """Проверяет, развернуто ли окружение."""
        return self in (self.STAGING, self.PRODUCTION)


class Config(BaseSettings):
    """Класс основных настроек приложения"""

    DATABASE_URL: str
    SITE_DOMAIN: str

    ENVIRONMENT: Environment = Environment.PRODUCTION

    CORS_ORIGINS: list[str]
    CORS_ORIGINS_REGEX: str | None = None
    CORS_HEADERS: list[str]

    APP_VERSION: str = "1"

    MIN_PASSWORD_LENGTH: int = 6
    MAX_PASSWORD_LENGTH: int = 128

    JWT_ALG: str
    JWT_SECRET: str
    JWT_EXP: int = 10  # minutes

    REFRESH_TOKEN_KEY: str = "refreshToken"
    REFRESH_TOKEN_EXP: int = 60 * 60 * 24 * 21  # 21 days

    SECURE_COOKIES: bool = True

    REDIS_URL: str = "redis://redis:6379"
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    API_REDIS_HOST: str = "api-redis"

    GOOGLE_BOOKS_API: str = "https://www.googleapis.com/books/v1"

    model_config = SettingsConfigDict(case_sensitive=True)


settings = Config()

app_configs: dict[str, Any] = {"title": "Library Management API"}

if settings.ENVIRONMENT.is_deployed:
    app_configs["root_path"] = f"/v{settings.APP_VERSION}"
