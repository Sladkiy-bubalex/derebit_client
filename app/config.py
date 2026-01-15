import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from loguru import logger

load_dotenv()


class Settings(BaseSettings):
    POSTGRES_HOST=os.getenv("POSTGRES_HOST")
    POSTGRES_PORT=os.getenv("POSTGRES_PORT")
    POSTGRES_DB=os.getenv("POSTGRES_DB")
    POSTGRES_USER=os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD=os.getenv("POSTGRES_PASSWORD")

    REDIS_HOST=os.getenv("REDIS_HOST")
    REDIS_PORT=os.getenv("REDIS_PORT")

    DERIBIT_BASE_URL: str = "https://test.deribit.com/api/v2/public"

    logger.add("file_app.log", level="INFO", rotation="10 MB", retention="1 week")

    @property
    def redis_url(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"

    @property
    def postgres_url(self) -> str:
        return (f"postgresql+asyncpg://{self.POSTGRES_USER}:"
                f"{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:"
                f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}")


def create_settings() -> Settings:
    return Settings()
