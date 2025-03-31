from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from config import settings
from repositories.base import AbstractUnitOfWork
from repositories.postgres.books import AuthorsRepository, BooksRepository

engine = create_async_engine(settings.DATABASE_URL, echo=True, future=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class PostgresUnitOfWork(AbstractUnitOfWork):
    def __init__(self):
        self.session: AsyncSession = None
        self.books = None
        self.authors = None

    async def __aenter__(self):  # ???
        self.session = async_session()
        self.books = BooksRepository(self)
        self.authors = AuthorsRepository(self)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            await self.session.rollback()
        else:
            await self.session.commit()
        await self.session.close()
