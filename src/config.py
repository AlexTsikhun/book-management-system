from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str | None = None
    SECRET_KEY: str = "your-secret-key"
    ALLOWED_GENRES: list = ["Fiction", "Non-Fiction", "Science", "History"]
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 3000000


settings = Settings()
