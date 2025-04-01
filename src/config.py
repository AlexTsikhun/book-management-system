from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str
    SECRET_KEY: str = "your-secret-key"
    ALLOWED_GENRES: list = ["Fiction", "Non-Fiction", "Science", "History"]


settings = Settings()
