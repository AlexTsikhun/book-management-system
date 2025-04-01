from .repository import FakeRepository


class BooksRepository(FakeRepository):
    pass


class AuthorsRepository(FakeRepository):
    async def retrieve_by_author_name(self, author_name: str):
        for item in self._items.values():
            if item.get("name") == author_name:
                return item
        return None
