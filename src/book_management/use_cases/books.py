from typing import Any

from book_management.services.books import FileParserFactory
from exceptions import DoesNotExistError, ValidationError
from repositories.base import AbstractUnitOfWork


class BaseBooksUseCase:
    def __init__(self, uow: AbstractUnitOfWork) -> None:  # ?
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
            author_id = await self.uow.authors.retrieve_by_name(author_name)
            print("author_id 11111111", author_id, type(author_id))

            if not author_id:
                author_id = await self.uow.authors.create({"name": author_name})
            print("author_id 22222222", author_id, type(author_id))

            book = await self.uow.books.create(
                {
                    "title": book_data["title"],
                    "author_id": author_id.id,  # ?
                    "genre": book_data["genre"].upper(),
                    "published_year": book_data["published_year"],
                }
            )

            return {
                "id": book.id,
                "title": book.title,
                "author_name": author_id.name,
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
            required_fields = ["title", "author_name", "genre", "published_year"]

            valid_books_data = []
            author_names = set()
            for book_data in books_data:
                if not all(field in book_data for field in required_fields):
                    missing_fields = [f for f in required_fields if f not in book_data]
                    failed_info.append(
                        {"data": book_data, "error": f"Missing required fields: {', '.join(missing_fields)}"}
                    )
                    continue
                valid_books_data.append(book_data)
                author_names.add(book_data["author_name"])

            if not valid_books_data:
                return {
                    "total_items": len(books_data),
                    "successful": 0,
                    "failed": len(failed_info),
                    "failed_info": failed_info,
                }

            existing_authors = await self.uow.authors.retrieve_by_names(list(author_names))
            author_map = {author.name: author for author in existing_authors}

            new_author_names = author_names - set(author_map.keys())
            if new_author_names:
                new_authors = await self.uow.authors.bulk_create([{"name": name} for name in new_author_names])
                author_map.update({author.name: author for author in new_authors})

            books_to_create = [
                {
                    "title": book_data["title"],
                    "author_id": author_map[book_data["author_name"]].id,
                    "genre": book_data["genre"].upper(),
                    "published_year": book_data["published_year"],
                }
                for book_data in valid_books_data
            ]
            imported_books = await self.uow.books.bulk_create(books_to_create)

            return {
                "total_items": len(books_data),
                "successful": len(imported_books),
                "failed": len(failed_info),
                "failed_info": failed_info,
            }
