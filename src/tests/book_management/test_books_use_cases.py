from book_management.use_cases.books import (
    CreateBookUseCase,
    DeleteBookUseCase,
    RetrieveBooksUseCase,
    RetrieveBookUseCase,
    UpdateBookUseCase,
)
from exceptions import DoesNotExistError
from tests.base import BaseTestCase


class RetrieveBooksUseCaseTestCase(BaseTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.use_case = RetrieveBooksUseCase(cls.uow)

    # async def test_retrieve_books_success(self):
    #     await self.uow.authors.create({"name": "Author 1"})
    #     await self.uow.books.create({"title": "Book 1", "author_id": 1, "genre": "Fiction", "published_year": 2000})
    #     await self.uow.books.create({"title": "Book 2", "author_id": 1, "genre": "Science", "published_year": 2010})

    #     result = await self.use_case(page=1, per_page=10, sort_by="title")

    #     self.assertEqual(len(result), 2)
    #     self.assertEqual(result[0]["title"], "Book 1")
    #     self.assertEqual(result[1]["title"], "Book 2")

    async def test_retrieve_books_empty(self):
        result = await self.use_case(page=1, per_page=10, sort_by="title")
        self.assertEqual(len(result), 0)


class CreateBookUseCaseTestCase(BaseTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.use_case = CreateBookUseCase(cls.uow)

    # async def test_create_book_success(self):
    #     await self.uow.authors.create({"name": "Author 1"})
    #     book_data = {
    #         "title": "New Book",
    #         "author_name": "Author 1",
    #         "genre": "Fiction",
    #         "published_year": 2020,
    #     }

    #     result = await self.use_case(book_data)
    #     self.assertEqual(result["title"], "New Book")
    #     # self.assertEqual(result["author_id"], 1)
    #     self.assertEqual(result["genre"], "Fiction")
    #     self.assertEqual(result["published_year"], 2020)
    #     self.assertEqual(result["id"], 1)


class RetrieveBookUseCaseTestCase(BaseTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.use_case = RetrieveBookUseCase(cls.uow)

    # async def test_retrieve_book_success(self):
    #     await self.uow.authors.create({"name": "Author 1"})
    #     await self.uow.books.create({"title": "Book 1", "author_id": 1, "genre": "Fiction", "published_year": 2000})

    #     result = await self.use_case(1)

    #     self.assertEqual(result["title"], "Book 1")
    #     self.assertEqual(result["id"], 1)

    async def test_retrieve_book_not_found(self):
        with self.assertRaises(DoesNotExistError):
            await self.use_case(999)


class UpdateBookUseCaseTestCase(BaseTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.use_case = UpdateBookUseCase(cls.uow)

    async def test_update_book_success(self):
        await self.uow.authors.create({"name": "Author 1"})
        await self.uow.books.create({"title": "Book 1", "author_id": 1, "genre": "Fiction", "published_year": 2000})

        book_data = {
            "title": "Updated Book",
            "author_name": "Author 1",
            "genre": "Science",
            "published_year": 2010,
        }

        result = await self.use_case(1, book_data)

        self.assertEqual(result["title"], "Updated Book")
        self.assertEqual(result["genre"], "Science")
        self.assertEqual(result["published_year"], 2010)
        # self.assertEqual(result["author_id"], 1)

    async def test_update_book_not_found(self):
        book_data = {
            "title": "Updated Book",
            "author_name": "Author 1",
            "genre": "Science",
            "published_year": 2010,
        }

        with self.assertRaises(DoesNotExistError):
            await self.use_case(999, book_data)

    async def test_update_book_author_not_found(self):
        await self.uow.books.create({"title": "Book 1", "author_id": 1, "genre": "Fiction", "published_year": 2000})
        book_data = {"author_name": "Unknown Author"}

        with self.assertRaises(DoesNotExistError):
            await self.use_case(1, book_data)


class DeleteBookUseCaseTestCase(BaseTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.use_case = DeleteBookUseCase(cls.uow)

    async def test_delete_book_success(self):
        a = await self.uow.authors.create({"name": "Author 1"})
        b = await self.uow.books.create(
            {"title": "Book 1", "author_id": a.id, "genre": "Fiction", "published_year": 2000}
        )

        result = await self.use_case(b.id)
        self.assertIsNone(result)

        book = await self.uow.books.retrieve(b.id)
        self.assertIsNone(book)

    async def test_delete_book_not_found(self):
        with self.assertRaises(DoesNotExistError):
            await self.use_case(999)
