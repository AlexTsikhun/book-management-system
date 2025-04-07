import pytest

from book_management.models import Genre
from book_management.use_cases.books import (
    BulkImportBooksUseCase,
    CreateBookUseCase,
    DeleteBookUseCase,
    ExportBooksUseCase,
    RetrieveBooksUseCase,
    RetrieveBookUseCase,
    UpdateBookUseCase,
)
from exceptions import DoesNotExistError


@pytest.mark.asyncio
class TestBookUseCases:
    async def test_create_book(self, uow):
        book_data = {
            "title": "Test Book",
            "author_name": "Test Author",
            "genre": Genre.FICTION.name,
            "published_year": 2020,
        }
        use_case = CreateBookUseCase(uow)
        result = await use_case(book_data)
        assert result["title"] == "Test Book"
        assert result["author_name"] == "Test Author"

    async def test_retrieve_books(self, uow):
        use_case = CreateBookUseCase(uow)
        await use_case(
            {"title": "Book1", "author_name": "Author1", "genre": Genre.FICTION.name, "published_year": 2020}
        )

        retrieve_use_case = RetrieveBooksUseCase(uow)
        result = await retrieve_use_case(page=1, per_page=10, sort_by="title:asc")
        assert len(result) > 0
        assert result[0]["title"] == "Book1"

    async def test_retrieve_book(self, uow):
        use_case = CreateBookUseCase(uow)
        book = await use_case(
            {"title": "Book2", "author_name": "Author2", "genre": Genre.SCIENCE.name, "published_year": 2021}
        )

        retrieve_use_case = RetrieveBookUseCase(uow)
        result = await retrieve_use_case(book["id"])
        assert result["title"] == "Book2"

    async def test_update_book(self, uow):
        use_case = CreateBookUseCase(uow)
        book = await use_case(
            {"title": "Book3", "author_name": "Author3", "genre": Genre.HISTORY.name, "published_year": 2022}
        )

        update_use_case = UpdateBookUseCase(uow)
        updated = await update_use_case(
            book["id"],
            {"title": "Updated Book", "author_name": "Author3", "genre": Genre.HISTORY.name, "published_year": 2022},
        )
        assert updated["title"] == "Updated Book"

    async def test_delete_book(self, uow):
        use_case = CreateBookUseCase(uow)
        book = await use_case(
            {"title": "Book4", "author_name": "Author4", "genre": Genre.NON_FICTION.name, "published_year": 2023}
        )

        delete_use_case = DeleteBookUseCase(uow)
        await delete_use_case(book["id"])

        retrieve_use_case = RetrieveBookUseCase(uow)
        with pytest.raises(DoesNotExistError):
            await retrieve_use_case(book["id"])

    async def test_bulk_import_books(self, uow):
        content = [{"title": "Bulk Book", "author_name": "Bulk Author", "genre": "FICTION", "published_year": 2024}]
        use_case = BulkImportBooksUseCase(uow)
        result = await use_case(content)
        assert result["successful"] == 1

    async def test_export_books(self, uow):
        use_case = CreateBookUseCase(uow)
        await use_case(
            {
                "title": "Export Book",
                "author_name": "Export Author",
                "genre": Genre.SCIENCE.name,
                "published_year": 2025,
            }
        )

        export_use_case = ExportBooksUseCase(uow)
        result = await export_use_case("json")
        assert "Export Book" in result
