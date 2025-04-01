from repositories.base import AbstractUnitOfWork
from repositories.fake.books import AuthorsRepository, BooksRepository


class FakeUnitOfWork(AbstractUnitOfWork):
    def __init__(self) -> None:
        self.books = BooksRepository()
        self.authors = AuthorsRepository()

    async def __aenter__(self):
        pass

    async def __aexit__(self, *args, **kwargs):
        pass
