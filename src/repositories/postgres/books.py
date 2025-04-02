from sqlalchemy import text

from book_management.models import Author, Book
from repositories.postgres.repository import PostgresRepository


class BooksRepository(PostgresRepository):
    model_class = Book

    async def retrieve(self, reference: int) -> dict | None:
        query = text(
            f"""
                SELECT b.id, b.title, a.name AS author_name, b.genre, b.published_year
                FROM {self.table_name} b
                JOIN authors a ON b.author_id = a.id
                WHERE b.id = :id
            """
        )
        result = await self.uow.session.execute(query, {"id": reference})
        return result.fetchone()

    async def get_all(self, offset: int, limit: int, sort_by: str) -> list[dict]:
        query = text(
            f"""
                SELECT b.id, b.title, a.name AS author_name, b.genre, b.published_year
                FROM {self.table_name} b
                JOIN authors a ON b.author_id = a.id
                ORDER BY {sort_by}
                OFFSET :offset LIMIT :limit
            """
        )
        result = await self.uow.session.execute(query, {"offset": offset, "limit": limit})
        return result.fetchall()


class AuthorsRepository(PostgresRepository):
    model_class = Author

    async def retrieve_by_author_name(self, author_name: str):
        query = text(f"SELECT * FROM {self.table_name} WHERE name = :name")
        result = await self.uow.session.execute(query, {"name": author_name})
        return result.fetchone()
