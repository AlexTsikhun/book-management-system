from datetime import datetime

from pydantic import BaseModel, field_validator


class BaseBookSchema(BaseModel):
    title: str
    author_name: str
    genre: str
    published_year: int


class BookCreateSchema(BaseBookSchema):
    @field_validator("published_year")
    def validate_year(cls, v):
        current_year = datetime.now().year
        if not 1800 <= v <= current_year:
            raise ValueError(f"Year must be between 1800 and {current_year}")
        return v


class BookResponseSchema(BaseBookSchema):
    id: int
