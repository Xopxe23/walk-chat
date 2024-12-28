from pydantic_settings import BaseSettings


class BaseConfig(BaseSettings):
    DOCKER: bool

    class Config:
        env_file = ".env"
        extra = "allow"
