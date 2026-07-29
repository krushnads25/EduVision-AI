from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "EduVision AI"
    DEBUG: bool = False
    DATABASE_URL: str
    DB_ECHO: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
