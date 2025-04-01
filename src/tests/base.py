import unittest
from unittest import mock

from repositories.fake.containers import FakeUnitOfWork

uow = FakeUnitOfWork()


class BaseTestCase(unittest.IsolatedAsyncioTestCase):
    __patchers = [
        mock.patch("dependencies.get_unit_of_work", new=mock.MagicMock(return_value=uow)),
    ]

    @classmethod
    def _start_patchers(cls, patchers: list):
        for patcher in patchers:
            patcher.start()

    @classmethod
    def _stop_patchers(cls, patchers: list):
        for patcher in patchers:
            patcher.stop()

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.uow = uow
        cls._start_patchers(cls.__patchers)
        cls.addClassCleanup(cls._stop_patchers, cls.__patchers)

    async def asyncSetUp(self):
        await super().asyncSetUp()
        # clean before each test
        self.uow.books._items.clear()
        self.uow.authors._items.clear()
        self.uow.books._id_counter = 1
        self.uow.authors._id_counter = 1

    async def asyncTearDown(self):
        await super().asyncTearDown()
        self.uow.books._items.clear()
        self.uow.authors._items.clear()
