from types import SimpleNamespace

from repositories.base import AbstractRepository


class FakeRepository(AbstractRepository):
    def __init__(self) -> None:
        self._items = {}
        self._id_counter = 1

    async def create(self, data: dict) -> SimpleNamespace:
        """Create a new item with auto-incrementing ID"""
        data["id"] = self._id_counter
        self._items[self._id_counter] = data.copy()
        self._id_counter += 1
        return SimpleNamespace(**data)

    async def retrieve(self, reference: int) -> SimpleNamespace | None:
        """Retrieve an item by ID"""
        if reference in self._items:
            return SimpleNamespace(**self._items[reference])
        return None

    async def update(self, reference: int, data: dict) -> SimpleNamespace | None:
        """Update an item by ID"""
        if reference in self._items:
            self._items[reference].update(data)
            return SimpleNamespace(**self._items[reference])
        return None

    async def delete(self, reference: int) -> None:
        """Delete an item by ID"""
        if reference in self._items:
            del self._items[reference]

    async def get_all(self, offset: int = 0, limit: int = 10, sort_by: str = "id") -> list[SimpleNamespace]:
        """Get all items with pagination and sorting"""
        items = list(self._items.values())
        items.sort(key=lambda x: x.get(sort_by, ""))
        paginated = items[offset : offset + limit]  # noqa
        return [SimpleNamespace(**item) for item in paginated]
