from app.config.base import BaseConfig


class SecretsConfig(BaseConfig):
    JWT_SECRET: str
    ALGORITHM: str
