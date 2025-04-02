from repositories.base import AbstractUnitOfWork
from repositories.fake.books import AuthorsRepository, BooksRepository, UsersRepository


class FakeUnitOfWork(AbstractUnitOfWork):
    def __init__(self) -> None:
        self.books = BooksRepository()
        self.authors = AuthorsRepository()
        self.users = UsersRepository()

    async def __aenter__(self):
        pass

    async def __aexit__(self, *args, **kwargs):
        pass
