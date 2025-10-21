from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache


class Settings(BaseSettings):
    # OpenAI
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")

    # App / DB
    database_url: str = Field(default="sqlite:///./local_business_ai.db", alias="DATABASE_URL")
    redis_url: str = Field(default="redis://localhost:6379", alias="REDIS_URL")
    secret_key: str = Field(default="dev_secret", alias="SECRET_KEY")
    debug: bool = Field(default=True, alias="DEBUG")
    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8000, alias="PORT")

    class Config:
        env_file = ".env"
        case_sensitive = False
        populate_by_name = True


@lru_cache
def get_settings() -> Settings:
    return Settings()


