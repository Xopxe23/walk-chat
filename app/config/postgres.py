from app.config.base import BaseConfig


class PostgresConfig(BaseConfig):
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    TEST_POSTGRES_DB: str

    @property
    def DB_URL(self) -> str:
        if self.DOCKER:
            self.POSTGRES_HOST = "db"
        return (f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
                f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}")

    @property
    def TEST_DB_URL(self):
        if self.DOCKER:
            self.POSTGRES_HOST = "db"
        return (f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
                f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.TEST_POSTGRES_DB}")
