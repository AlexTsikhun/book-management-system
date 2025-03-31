from typing import Any, Dict

from repositories.postgres.container import PostgresUnitOfWork


class BaseBooksUseCase:
    def __init__(self, uow: PostgresUnitOfWork) -> None:
        self.uow = uow


class RetrieveBooksUseCase(BaseBooksUseCase):
    async def __call__(self, page: int, per_page: int, sort_by: str) -> Dict[str, Any]:
        async with self.uow:
            books_data = await self.uow.books.get_all(offset=(page - 1) * per_page, limit=per_page, sort_by=sort_by)
            print("books_dwwwwwwwwwwwata", books_data)

            return {
                "books": books_data,
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                },
            }


class CreateBookUseCase(BaseBooksUseCase):
    async def __call__(self, page: int, per_page: int, sort_by: str) -> Dict[str, Any]:
        pass
