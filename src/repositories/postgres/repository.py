from sqlalchemy import text

from repositories.base import AbstractRepository


class PostgresRepository(AbstractRepository):
    model_class = None

    def __init__(self, uow, id_field: str = "id"):
        self.uow = uow
        self.id_field = id_field
        self.table_name = self.model_class.__tablename__

    async def create(self, data: dict) -> dict:
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

    async def retrieve(self, reference: int) -> dict | None:
        query = text(f"SELECT * FROM {self.table_name} WHERE {self.id_field} = :id")
        result = await self.uow.session.execute(query, {"id": reference})
        return result.fetchone()

    async def update(self, reference: int, data: dict) -> dict:
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

    async def bulk_create(self, data: list[dict]) -> list[dict]:
        """ Create multiple rows at once """
        if not data:
            return []

        fields = list(data[0].keys())
        field_names = ", ".join(fields)

        placeholders = []
        params = {}
        for i, item in enumerate(data):
            row_placeholders = [f":val_{i}_{field}" for field in fields]
            placeholders.append(f"({', '.join(row_placeholders)})")
            for field in fields:
                params[f"val_{i}_{field}"] = item[field]

        values_clause = ", ".join(placeholders)
        query = text(
            f"""
            INSERT INTO {self.table_name} ({field_names})
            VALUES {values_clause}
            RETURNING *;
        """
        )

        result = await self.uow.session.execute(query, params)
        return result.scalars().all()

    async def get_all(self, offset: int, limit: int, sort_by: str="id") -> list[dict]:
        query = text(
            f"""
            SELECT * FROM {self.table_name}
            ORDER BY {sort_by}
            OFFSET :offset LIMIT :limit
        """
        )
        result = await self.uow.session.execute(query, {"offset": offset, "limit": limit})
        return result.fetchall()
