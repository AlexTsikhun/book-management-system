from types import SimpleNamespace
from .repository import FakeRepository


class BooksRepository(FakeRepository):
    pass


class AuthorsRepository(FakeRepository):
    async def retrieve_by_name(self, author_name: str):
        for item in self._items.values():
            if item.get("name") == author_name:
                return SimpleNamespace(**item)
        return None

class UsersRepository(FakeRepository):
    async def retrieve_by_username(self, username: str):
        for item in self._items.values():
            if item.get("username") == username:
                return SimpleNamespace(**item)
        return None

    async def retrieve_by_email(self, email: str):
        for item in self._items.values():
            if item.get("email") == email:
                return SimpleNamespace(**item)
        return None
    