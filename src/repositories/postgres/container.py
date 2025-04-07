from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from repositories.base import AbstractUnitOfWork
from repositories.postgres.books import AuthorsRepository, BooksRepository, UsersRepository


class PostgresUnitOfWork(AbstractUnitOfWork):
    def __init__(self, engine=None):
        self._engine = engine
        self._session_factory = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        self.session = None

        self.books = BooksRepository(self)
        self.authors = AuthorsRepository(self)
        self.users = UsersRepository(self)

    async def __aenter__(self):
        if not hasattr(self, "session") or self.session is None:
            self.session = self._session_factory()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if hasattr(self, "_session_factory") and self.session:
            if exc_type is not None:
                await self.session.rollback()
            else:
                await self.session.commit()
            await self.session.close()
            self.session = None
