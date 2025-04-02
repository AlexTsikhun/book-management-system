from typing import Any

from book_management.services.books import FileParserFactory
from exceptions import DoesNotExistError, ValidationError
from repositories.base import AbstractUnitOfWork


class BaseBooksUseCase:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self.uow = uow


class RetrieveBooksUseCase(BaseBooksUseCase):
    async def __call__(self, page: int, per_page: int, sort_by: str) -> dict[str, Any]:
        async with self.uow:
            books_data = await self.uow.books.get_all(offset=(page - 1) * per_page, limit=per_page, sort_by=sort_by)
            return books_data


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


class BulkImportBooksUseCase(BaseBooksUseCase):
    async def __call__(self, file_content: str, filename: str) -> dict[str, Any]:
        async with self.uow:
            parser = FileParserFactory.get_parser(filename)
            try:
                books_data = parser.parse(file_content)
            except ValueError as error:
                raise ValidationError("file", f"File parsing error: {str(error)}")
            except TypeError:
                raise ValidationError("file", "Missing required field")

            imported_books = []
            failed_info = []

            for book_data in books_data:
                required_fields = ["title", "author_name", "genre", "published_year"]
                if not all(field in book_data for field in required_fields):
                    missing_fields = [f for f in required_fields if f not in book_data]
                    failed_info.append(
                        {"data": book_data, "error": f"Missing required fields: {', '.join(missing_fields)}"}
                    )
                    continue

                author_name = book_data["author_name"]
                author = await self.uow.authors.retrieve_by_author_name(author_name)

                if not author:
                    author = await self.uow.authors.create({"name": author_name})
                else:
                    author = await self.uow.authors.retrieve(author.id)

                book = await self.uow.books.create(
                    {
                        "title": book_data["title"],
                        "author_id": author.id,
                        "genre": book_data["genre"].upper(),
                        "published_year": book_data["published_year"],
                    }
                )
                imported_books.append(book)

            return {
                "total_items": len(books_data),
                "successful": len(imported_books),
                "failed": len(failed_info),
                "failed_info": failed_info,
            }
