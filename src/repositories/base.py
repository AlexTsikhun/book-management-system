import abc


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def create(self, data: dict):
        raise NotImplementedError()

    @abc.abstractmethod
    def retrieve(self, reference):
        raise NotImplementedError()

    @abc.abstractmethod
    def update(self, reference, data: dict):
        raise NotImplementedError()

    @abc.abstractmethod
    def delete(self, reference):
        raise NotImplementedError()


class AbstractUnitOfWork(abc.ABC):
    shops: AbstractRepository

    @abc.abstractmethod
    async def __aenter__(self):
        raise NotImplementedError()

    @abc.abstractmethod
    async def __aexit__(self, *args, **kwargs):
        raise NotImplementedError()
