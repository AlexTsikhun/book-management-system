from typing import Dict, Iterable, List, Optional

from sqlalchemy import text

from repositories.base import AbstractRepository


class PostgresRepository(AbstractRepository):
    model_class = None

    def __init__(self, uow, id_field: str = "id"):
        self.uow = uow
        self.id_field = id_field
        self.table_name = self.model_class.__tablename__

    async def create(self, data: Dict) -> Dict:
        fields = ", ".join(data.keys())
        placeholders = ", ".join(f":{key}" for key in data.keys())
        query = text(
            f"""
            INSERT INTO {self.table_name} ({fields})
            VALUES ({placeholders})
            RETURNING *
        """
        )
        result = await self.uow.session.execute(query, data)
        return result.fetchone()

    async def retrieve(self, reference: int) -> Optional[Dict]:
        query = text(f"SELECT * FROM {self.table_name} WHERE {self.id_field} = :id")
        result = await self.uow.session.execute(query, {"id": reference})
        return result.fetchone()

    async def update(self, reference: int, data: Dict) -> Dict:
        set_clause = ", ".join(f"{key} = :{key}" for key in data.keys())
        query = text(
            f"""
            UPDATE {self.table_name}
            SET {set_clause}
            WHERE {self.id_field} = :id
            RETURNING *
        """
        )
        result = await self.uow.session.execute(query, {**data, "id": reference})
        return result.fetchone()

    async def delete(self, reference: int) -> None:
        query = text(f"DELETE FROM {self.table_name} WHERE {self.id_field} = :id")
        await self.uow.session.execute(query, {"id": reference})

    async def bulk_create(self, data: Iterable[Dict]) -> List[Dict]:
        if not data:
            return []
        fields = ", ".join(data[0].keys())
        placeholders = ", ".join(f":{key}" for key in data[0].keys())
        query = text(
            f"""
            INSERT INTO {self.table_name} ({fields})
            VALUES ({placeholders})
            RETURNING *
        """
        )
        result = await self.uow.session.execute(query, list(data))
        return result.fetchall()

    async def get_all(self, offset: int, limit: int, sort_by: str) -> List[Dict]:
        query = text(
            f"""
            SELECT * FROM {self.table_name}
            ORDER BY {sort_by}
            OFFSET :offset LIMIT :limit
        """
        )
        result = await self.uow.session.execute(query, {"offset": offset, "limit": limit})
        return result.fetchall()

    # Додатковий метод для специфічних випадків (наприклад, join з authors)
    async def get_books_with_authors(self, offset: int, limit: int, sort_by: str) -> List[Dict]:
        query = text(
            f"""
            SELECT b.*, a.name as author_name
            FROM {self.table_name} b
            JOIN authors a ON b.author_id = a.id
            ORDER BY {sort_by}
            OFFSET :offset LIMIT :limit
        """
        )
        result = await self.uow.session.execute(query, {"offset": offset, "limit": limit})
        return result.fetchall()
