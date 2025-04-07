import asyncio
import enum

import pytest
from sqlalchemy.ext.asyncio import create_async_engine
from testcontainers.postgres import PostgresContainer

from book_management import Base
from repositories.postgres.container import PostgresUnitOfWork


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def postgres_container():
    postgres = PostgresContainer("postgres:15-alpine")
    with postgres:
        yield postgres


@pytest.fixture(scope="session")
async def async_engine(postgres_container):
    db_url = postgres_container.get_connection_url().replace("psycopg2", "asyncpg")
    engine = create_async_engine(db_url, echo=True)
    yield engine
    await engine.dispose()


@pytest.fixture
async def uow(async_engine):
    uow = PostgresUnitOfWork(engine=async_engine)
    await uow.__aenter__()

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield uow

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await uow.__aexit__(None, None, None)
