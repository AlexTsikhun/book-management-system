from typing import Any

from book_management.models import Genre
from book_management.services.books import FileExporterFactory
from book_management.services.recommendation import RecommendationService
from book_management.services.validators import BookQueryValidator
from exceptions import DoesNotExistError
from repositories.base import AbstractUnitOfWork


class BaseBooksUseCase:
    def __init__(self, uow: AbstractUnitOfWork) -> None:  # ?
        self.uow = uow


class RetrieveBooksUseCase(BaseBooksUseCase):
    async def __call__(self, page: int, per_page: int, sort_by: str) -> dict[str, Any]:
        async with self.uow:
            field, direction = BookQueryValidator.parse_sort_by(sort_by)

            offset = (page - 1) * per_page
            books_data = await self.uow.books.get_all(
                offset=offset, limit=per_page, sort_field=field, sort_direction=direction
            )
            return books_data


class CreateBookUseCase(BaseBooksUseCase):
    async def __call__(self, book_data: dict) -> dict[str, Any]:
        async with self.uow:
            author_name = book_data["author_name"]
            author = await self.uow.authors.retrieve_by_name(author_name)

            if not author:
                author = await self.uow.authors.create({"name": author_name})

            book = await self.uow.books.create(
                {
                    "title": book_data["title"],
                    "author_id": author.id,  # ?
                    "genre": book_data["genre"],
                    "published_year": book_data["published_year"],
                }
            )

            return {
                "id": book.id,
                "title": book.title,
                "author_name": author.name,
                "genre": book.genre,
                "published_year": book.published_year,
            }


class RetrieveBookUseCase(BaseBooksUseCase):
    async def __call__(self, book_id: int) -> dict[str, Any] | None:
        async with self.uow:
            book = await self.uow.books.retrieve(book_id)

            if not book:
                raise DoesNotExistError()

            return {
                "id": book.id,
                "title": book.title,
                "author_name": book.author.name,
                "genre": book.genre,
                "published_year": book.published_year,
            }


class UpdateBookUseCase(BaseBooksUseCase):
    async def __call__(self, book_id: int, book_data: dict) -> dict[str, Any] | None:
        async with self.uow:
            author_name = book_data["author_name"]
            author = await self.uow.authors.retrieve_by_name(author_name)

            if not author:
                raise DoesNotExistError()

            book_data["author_id"] = author.id

            updated_book = await self.uow.books.update(book_id, book_data)
            if not updated_book:
                raise DoesNotExistError()

            return {
                "id": updated_book.id,
                "title": updated_book.title,
                "author_name": author.name,
                "genre": updated_book.genre,
                "published_year": updated_book.published_year,
            }


class DeleteBookUseCase(BaseBooksUseCase):
    async def __call__(self, book_id: int) -> None:
        async with self.uow:
            book = await self.uow.books.retrieve(book_id)

            if not book:
                raise DoesNotExistError()

            await self.uow.books.delete(book.id)


class BulkImportBooksUseCase(BaseBooksUseCase):
    async def __call__(self, valid_books: list) -> dict[str, Any]:
        async with self.uow:
            if not valid_books:
                return {
                    "successful": 0,
                }

            author_names = {book_data["author_name"] for book_data in valid_books}
            existing_authors = await self.uow.authors.retrieve_by_names(author_names)
            author_map = {author.name: author for author in existing_authors}

            new_author_names = author_names - set(author_map.keys())
            if new_author_names:
                new_authors = await self.uow.authors.bulk_create([{"name": name} for name in new_author_names])
                author_map.update({author.name: author for author in new_authors})

            books_to_create = [
                {
                    "title": book_data["title"],
                    "author_id": author_map[book_data["author_name"]].id,
                    "genre": book_data["genre"],
                    "published_year": book_data["published_year"],
                }
                for book_data in valid_books
            ]
            imported_books = await self.uow.books.bulk_create(books_to_create)

            return {
                "successful": len(imported_books),
            }


class ExportBooksUseCase(BaseBooksUseCase):
    async def __call__(self, format: str):
        async with self.uow:
            books = await self.uow.books.get_all(offset=0, limit=1000)

            books_data = [
                {
                    "id": book.id,
                    "title": book.title,
                    "author_name": book.author_name,
                    "genre": book.genre.value if isinstance(book.genre, Genre) else book.genre,
                    "published_year": book.published_year,
                }
                for book in books
            ]

            exporter = FileExporterFactory.get_exporter(format)
            return exporter.export(books_data)


class RecommendBooksUseCase(BaseBooksUseCase):
    async def __call__(self, book_id: int, limit: int = 5) -> list[dict[str, Any]]:
        async with self.uow:
            books = await self.uow.books.get_all(offset=0, limit=1000)
            if not books:
                raise DoesNotExistError()

            target_book = await self.uow.books.retrieve(book_id)
            if not target_book:
                raise DoesNotExistError(f"Book with id {book_id} does not exist")

            book_texts = [f"{book.title} {book.genre} {book.author_name}" for book in books]
            target_text = f"{target_book.title} {target_book.genre} {target_book.author_name}"
            book_ids = [book.id for book in books]

            recommendation_service = RecommendationService()
            recommended_ids = recommendation_service.get_recommendations(target_text, book_texts, book_ids, limit)

            recommendations = [
                {
                    "id": book.id,
                    "title": book.title,
                    "author_name": book.author_name,
                    "genre": book.genre,
                    "published_year": book.published_year,
                }
                for book in books
                if book.id in recommended_ids
            ]

            return recommendations
