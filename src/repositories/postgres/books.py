from sqlalchemy import text

from auth.models import User
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

    async def get_all(self, offset: int, limit: int , sort_by: str = "id") -> list[dict]:
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

    async def retrieve_by_name(self, author_name: str):
        query = text(f"SELECT * FROM {self.table_name} WHERE name = :name")
        result = await self.uow.session.execute(query, {"name": author_name})
        return result.fetchone()

    async def retrieve_by_names(self, author_names: list[str]):
        query = text(f"SELECT * FROM {self.table_name} WHERE name = ANY(:names)")
        result = await self.uow.session.execute(query, {"names": author_names})
        return result.fetchall()


class UsersRepository(PostgresRepository):
    model_class = User

    async def retrieve_by_username(self, username: str):
        query = text(f"SELECT * FROM {self.table_name} WHERE username = :username")
        result = await self.uow.session.execute(query, {"username": username})
        return result.fetchone()
    
    async def retrieve_by_email(self, email: str):
        query = text(f"SELECT * FROM {self.table_name} WHERE email = :email")
        result = await self.uow.session.execute(query, {"email": email})
        return result.fetchone()