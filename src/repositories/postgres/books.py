from typing import Iterable

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

    async def get_all(
        self, offset: int, limit: int | None, sort_field: str = "id", sort_direction: str = "asc"
    ) -> list[dict]:
        _sort_field_mapping = {
            "id": "b.id",
            "title": "b.title",
            "published_year": "b.published_year",
            "author": "a.name",
        }

        order_column = _sort_field_mapping.get(sort_field, "b.id")
        order_by_clause = f"ORDER BY {order_column} {sort_direction}"

        query = text(
            f"""
                SELECT
                    b.id,
                    b.title,
                    a.name AS author_name,
                    b.genre,
                    b.published_year
                FROM {self.table_name} b
                JOIN authors a ON b.author_id = a.id
                {order_by_clause}
                OFFSET :offset {'LIMIT :limit' if limit is not None else ''}
            """
        )

        params = {"offset": offset}
        if limit is not None:
            params["limit"] = limit
        result = await self.uow.session.execute(query, params)
        return result.mappings().all()


class AuthorsRepository(PostgresRepository):
    model_class = Author

    async def retrieve_by_name(self, author_name: str):
        query = text(f"SELECT * FROM {self.table_name} WHERE name = :name")
        result = await self.uow.session.execute(query, {"name": author_name})
        return result.fetchone()

    async def retrieve_by_names(self, author_names: Iterable[str]):
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
