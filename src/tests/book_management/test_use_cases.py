from datetime import datetime, timezone

import pytest

from book_management.models import Genre
from book_management.use_cases.books import CreateBookUseCase, DeleteBookUseCase, RetrieveBookUseCase, UpdateBookUseCase
from exceptions import DoesNotExistError
from repositories.fake.containers import FakeUnitOfWork


class BaseBookTestCase:
    @pytest.fixture(autouse=True)
    async def setup(self):
        self.uow = FakeUnitOfWork()

        # Create test author
        self.test_author = {"id": 1, "name": "Test Author", "created_at": datetime.now(timezone.utc)}
        await self.uow.authors.create(self.test_author)

        # Create test book
        self.test_book = {
            "id": 1,
            "title": "Test Book",
            "author_id": self.test_author["id"],
            "genre": Genre.FICTION,
            "published_year": 2024,
        }
        await self.uow.books.create(self.test_book)

    def book_data(self) -> dict:
        """Helper method to generate book data for tests"""
        return {
            "title": "New Test Book",
            "author_id": self.test_author["id"],
            "genre": Genre.FICTION,
            "published_year": 2024,
        }


class TestCreateBookUseCase(BaseBookTestCase):
    async def test_create_book(self):
        use_case = CreateBookUseCase(self.uow)
        result = await use_case(self.book_data())
        assert result["title"] == self.book_data()["title"]
        assert result["author_id"] == self.test_author["id"]


class TestRetrieveBookUseCase(BaseBookTestCase):
    async def test_retrieve_book(self):
        use_case = RetrieveBookUseCase(self.uow)
        result = await use_case(self.test_book["id"])
        assert result["id"] == self.test_book["id"]
        assert result["title"] == self.test_book["title"]


class TestUpdateBookUseCase(BaseBookTestCase):
    async def test_update_book(self):
        use_case = UpdateBookUseCase(self.uow)
        updated_data = {"title": "Updated Title"}
        result = await use_case(self.test_book["id"], updated_data)
        assert result["title"] == updated_data["title"]


class TestDeleteBookUseCase(BaseBookTestCase):
    async def test_delete_book(self):
        use_case = DeleteBookUseCase(self.uow)
        await use_case(self.test_book["id"])
        with pytest.raises(DoesNotExistError):
            await self.uow.books.retrieve(self.test_book["id"])
