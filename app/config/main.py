from app.config.postgres import PostgresConfig
from app.config.secret import SecretsConfig


class AppSettings:
    def __init__(self):
        self.postgres = PostgresConfig()
        self.secret = SecretsConfig()


settings = AppSettings()
