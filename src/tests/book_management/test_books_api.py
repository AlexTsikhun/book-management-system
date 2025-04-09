import json

import pytest
from httpx import AsyncClient

from book_management.models import Genre
from dependencies import get_unit_of_work
from main import application
from repositories.postgres.container import PostgresUnitOfWork
from tests.base import BaseAPITest


@pytest.mark.asyncio
class TestBooksAPI(BaseAPITest):
    async def test_create_book_success(self, client: AsyncClient, override_dependencies):
        book_data = {
            "title": "New Book",
            "author_name": "New Author",
            "genre": Genre.SCIENCE.value,
            "published_year": 2024,
        }
        response = await client.post("/books/", json=book_data)

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "New Book"
        assert data["genre"] == "Science"
        assert data["id"] is not None

    async def test_create_book_invalid_genre(self, client: AsyncClient, override_dependencies):
        book_data = {
            "title": "Invalid Genre Book",
            "author_name": "Author",
            "genre": "InvalidGenre",
            "published_year": 2023,
        }
        response = await client.post("/books/", json=book_data)
        assert response.status_code == 422
        assert "Input should be" in response.text

    async def test_retrieve_books_success(self, client: AsyncClient, override_dependencies):
        await self._create_book(client, "Book A")
        await self._create_book(client, "Book B")

        response = await client.get("/books/?page=1&per_page=10&sort_by=title:asc")
        assert response.status_code == 200
        books = response.json()
        assert len(books) >= 2
        assert books[0]["title"] == "Book A"
        assert books[1]["title"] == "Book B"

    async def test_retrieve_books_invalid_sort(self, client: AsyncClient, override_dependencies):
        response = await client.get("/books/?sort_by=invalid:asc")
        assert response.status_code == 400
        assert "Invalid field 'invalid'" in response.text

    async def test_retrieve_book_success(self, client: AsyncClient, override_dependencies):
        book = await self._create_book(client, "Single Book")
        response = await client.get(f"/books/{book['id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == book["id"]
        assert data["title"] == "Single Book"

    async def test_retrieve_book_not_found(self, client: AsyncClient, override_dependencies):
        response = await client.get("/books/9999")
        assert response.status_code == 404
        assert "Not found." in response.text

    async def test_update_book_success(self, client: AsyncClient, override_dependencies):
        book = await self._create_book(client, "Old Title")
        update_data = {
            "id": book["id"],
            "title": "New Title",
            "author_name": "Test Author",
            "genre": Genre.FICTION.value,
            "published_year": 2023,
        }
        response = await client.put(f"/books/{book['id']}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "New Title"
        assert data["id"] == book["id"]

    async def test_update_book_not_found(self, client: AsyncClient, override_dependencies):
        update_data = {
            "id": 9999,
            "title": "New Title",
            "author_name": "Test Author",
            "genre": Genre.FICTION.value,
            "published_year": 2023,
        }
        response = await client.put("/books/9999", json=update_data)
        assert response.status_code == 404
        assert "Not found." in response.text

    async def test_delete_book_success(self, client: AsyncClient, override_dependencies):
        book = await self._create_book(client, "To Delete")
        response = await client.delete(f"/books/{book['id']}")
        assert response.status_code == 204

        response = await client.get(f"/books/{book['id']}")
        assert response.status_code == 404

    async def test_delete_book_not_found(self, client: AsyncClient, override_dependencies):
        response = await client.delete("/books/9999")
        assert response.status_code == 404
        assert "Not found." in response.text

    async def test_export_books_json_success(self, client: AsyncClient, override_dependencies):
        await self._create_book(client, "Export Book")
        response = await client.get("/books/export?format=json")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        data = json.loads(response.text)
        assert any(book["title"] == "Export Book" for book in data)

    async def test_export_books_invalid_format(self, client: AsyncClient, override_dependencies):
        response = await client.get("/books/export?format=xml")
        assert response.status_code == 400
        assert "Format must be 'json' or 'csv'" in response.text

    async def test_bulk_import_books_success(self, client: AsyncClient, override_dependencies):
        csv_content = "title,author_name,genre,published_year\nBulk Book,Bulk Author,Fiction,2024"
        response = await client.post(
            "/books/bulk-import",
            files={"file": ("books.csv", csv_content, "text/csv")},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["successful"] == 1
        assert data["failed"] == 0

    async def test_bulk_import_books_invalid_file(self, client: AsyncClient, override_dependencies):
        response = await client.post(
            "/books/bulk-import",
            files={"file": ("books.txt", "invalid content", "text/plain")},
        )
        assert response.status_code == 400
        assert "Please ensure the file is in JSON or CSV format" in response.text

    async def test_recommend_books_success(self, client: AsyncClient, override_dependencies):
        book1 = await self._create_book(client, "Book 1", Genre.FICTION.value)
        await self._create_book(client, "Book 2", Genre.SCIENCE.value)
        await self._create_book(client, "Book 3", Genre.FICTION.value)

        response = await client.get(f"/books/recommendations/{book1['id']}?limit=1")
        assert response.status_code == 200
        recommendations = response.json()
        assert len(recommendations) == 1
        assert recommendations[0]["genre"] == Genre.FICTION.value  # Should recommend similar book

    async def test_recommend_books_not_found(self, client: AsyncClient, override_dependencies):
        response = await client.get("/books/recommendations/9999")
        assert response.status_code == 404
        assert "Not found." in response.text

    async def test_create_book_unauthorized(self, client: AsyncClient, uow: PostgresUnitOfWork):
        application.dependency_overrides[get_unit_of_work] = lambda: uow

        book_data = {
            "title": "Unauthorized Book",
            "author_name": "Author",
            "genre": Genre.FICTION.value,
            "published_year": 2023,
        }
        response = await client.post("/books/", json=book_data)
        assert response.status_code == 401
        application.dependency_overrides.clear()
