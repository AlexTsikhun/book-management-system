from typing import Any

from exceptions import DoesNotExistError
from repositories.base import AbstractUnitOfWork


class BaseBooksUseCase:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self.uow = uow


class RetrieveBooksUseCase(BaseBooksUseCase):
    async def __call__(self, page: int, per_page: int, sort_by: str) -> dict[str, Any]:
        async with self.uow:
            books_data = await self.uow.books.get_all(offset=(page - 1) * per_page, limit=per_page, sort_by=sort_by)
            return {
                "books": books_data,
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                },
            }


class CreateBookUseCase(BaseBooksUseCase):
    async def __call__(self, book_data: dict) -> dict[str, Any]:
        async with self.uow:
            author_name = book_data["author_name"]
            author_id = await self.uow.authors.retrieve_by_author_name(author_name)

            if not author_id:
                raise DoesNotExistError()

            return await self.uow.books.create(
                {
                    "title": book_data["title"],
                    "author_id": author_id["id"],  # ?
                    "genre": book_data["genre"],
                    "published_year": book_data["published_year"],
                }
            )


class RetrieveBookUseCase(BaseBooksUseCase):
    async def __call__(self, book_id: int) -> dict[str, Any] | None:
        async with self.uow:
            book = await self.uow.books.retrieve(book_id)

            if not book:
                raise DoesNotExistError()

            return book


class UpdateBookUseCase(BaseBooksUseCase):
    async def __call__(self, book_id: int, book_data: dict) -> dict[str, Any] | None:
        async with self.uow:
            # If author_name is provided, get or create author
            if "author_name" in book_data:
                author_name = book_data.pop("author_name")
                author_id = await self.uow.authors.retrieve_by_author_name(author_name)

                if not author_id:
                    raise DoesNotExistError()

                book_data["author_id"] = author_id["id"]

            updated_book = await self.uow.books.update(book_id, book_data)
            if not updated_book:
                raise DoesNotExistError()

            return updated_book


class DeleteBookUseCase(BaseBooksUseCase):
    async def __call__(self, book_id: int) -> None:
        async with self.uow:
            book = await self.uow.books.retrieve(book_id)

            if not book:
                raise DoesNotExistError()

            await self.uow.books.delete(book.id)
