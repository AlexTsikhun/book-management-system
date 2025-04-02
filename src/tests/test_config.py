from pydantic_settings import BaseSettings


class _TestSettings(BaseSettings):
    """Test settings with dummy values for testing"""

    DATABASE_URL: str = "postgresql+asyncpg://test:test@localhost:5432/test_db"
    SECRET_KEY: str = "test-secret-key"
    ALLOWED_GENRES: list = ["Fiction", "Non-Fiction", "Science", "History"]

    model_config = {"env_file": None, "extra": "forbid"}
