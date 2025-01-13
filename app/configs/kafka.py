from app.configs.base import BaseConfig


class KafkaConfig(BaseConfig):
    KAFKA_HOST: str
    KAFKA_PORT: int

    @property
    def KAFKA_URL(self):
        if self.DOCKER:
            self.KAFKA_HOST = "kafka"
        return f"{self.KAFKA_HOST}:{self.KAFKA_PORT}"
