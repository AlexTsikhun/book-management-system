import os

from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine

from auth.services import get_active_current_user, oauth2_scheme
from config import settings


def get_unit_of_work():
    if os.getenv("ENV") == "test":
        from repositories.fake.containers import FakeUnitOfWork

        return FakeUnitOfWork()

    from repositories.postgres.container import PostgresUnitOfWork

    engine = create_async_engine(settings.DATABASE_URL, echo=True, future=True)

    return PostgresUnitOfWork(engine)


async def get_current_user(token: str = Depends(oauth2_scheme), uow=Depends(get_unit_of_work)):
    return await get_active_current_user(token, uow)
