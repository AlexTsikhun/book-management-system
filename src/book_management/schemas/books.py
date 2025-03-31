from pydantic import BaseModel, field_validator


class BookCreateSchema(BaseModel):
    title: str
    author_name: str
    genre: str
    published_year: int

    @field_validator("published_year")
    def validate_year(cls, v):
        if not 1800 <= v <= 2025:
            raise ValueError("Year must be between 1800 and 2025")
        return v


class BookResponseSchema(BaseModel):
    id: int
    title: str
    author_name: str
    genre: str
    published_year: int
