from pydantic_settings import BaseSettings


class BaseConfig(BaseSettings):
    MODE: str

    class Config:
        env_file = ".env"
        extra = "allow"
