from sqlalchemy import text

from book_management.models import Author, Book
from repositories.postgres.repository import PostgresRepository


class BooksRepository(PostgresRepository):
    model_class = Book


class AuthorsRepository(PostgresRepository):
    model_class = Author

    async def retrieve_by_author_name(self, author_name: str):
        query = text(f"SELECT * FROM {self.table_name} WHERE name = :name")
        result = await self.uow.session.execute(query, {"name": author_name})
        return result.fetchone()
