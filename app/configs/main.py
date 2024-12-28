from app.configs.kafka import KafkaConfig
from app.configs.postgres import PostgresConfig
from app.configs.secret import SecretsConfig


class AppSettings:
    def __init__(self):
        self.postgres = PostgresConfig()
        self.secret = SecretsConfig()
        self.kafka = KafkaConfig()


settings = AppSettings()
