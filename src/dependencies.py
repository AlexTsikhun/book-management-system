from fastapi import Depends
from sqlalchemy.exc import ArgumentError
from sqlalchemy.ext.asyncio import create_async_engine

from auth.services import get_active_current_user, oauth2_scheme
from config import settings
from repositories.postgres.container import PostgresUnitOfWork

# In order not to create an engine every time I call get_unit_of_work,
# I call it this way and catch the error of missing `DATABASE_URL`
try:
    engine = create_async_engine(settings.DATABASE_URL, echo=True, future=True)
except ArgumentError:
    print("ArgumentError")


def get_unit_of_work():
    return PostgresUnitOfWork(engine)


async def get_current_user(token: str = Depends(oauth2_scheme), uow=Depends(get_unit_of_work)):
    return await get_active_current_user(token, uow)
