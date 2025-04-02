from datetime import datetime

from pydantic import BaseModel, field_validator


class BaseBookSchema(BaseModel):
    title: str
    author_name: str
    genre: str
    published_year: int


class BookCreateSchema(BaseBookSchema):
    @field_validator("published_year")
    def validate_year(cls, year: int):
        current_year = datetime.now().year
        if not 1800 <= year <= current_year:
            raise ValueError(f"Year must be between 1800 and {current_year}")
        return year


class BookResponseSchema(BaseBookSchema):
    id: int


class BookBulkImportResponse(BaseModel):
    total_items: int
    successful: int
    failed: int
    failed_info: list
