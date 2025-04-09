import fakeredis.aioredis
import pytest_asyncio
from fastapi_limiter import FastAPILimiter
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine
from testcontainers.postgres import PostgresContainer

from book_management import Base
from dependencies import get_current_user, get_unit_of_work
from main import application
from repositories.postgres.container import PostgresUnitOfWork


@pytest_asyncio.fixture(scope="session")
def postgres_container():
    postgres = PostgresContainer("postgres:15-alpine")
    with postgres:
        yield postgres


@pytest_asyncio.fixture(loop_scope="function", scope="function")
async def async_engine(postgres_container):
    db_url = postgres_container.get_connection_url().replace("psycopg2", "asyncpg")
    engine = create_async_engine(db_url)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(loop_scope="function", scope="function")
async def uow(async_engine):
    uow = PostgresUnitOfWork(engine=async_engine)
    await uow.__aenter__()

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield uow

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await uow.__aexit__(None, None, None)


@pytest_asyncio.fixture(loop_scope="function", scope="function", autouse=True)
async def setup_limiter():
    redis = fakeredis.aioredis.FakeRedis()
    await FastAPILimiter.init(redis)
    yield
    await redis.close()


@pytest_asyncio.fixture(loop_scope="function", scope="function")
async def client():
    async with AsyncClient(app=application, base_url="http://test") as async_client:
        yield async_client


@pytest_asyncio.fixture(loop_scope="function", scope="function")
def mock_current_user():
    return {"username": "testuser", "email": "test@example.com"}


@pytest_asyncio.fixture(loop_scope="function", scope="function")
def override_dependencies(mock_current_user, uow):
    application.dependency_overrides[get_unit_of_work] = lambda: uow
    application.dependency_overrides[get_current_user] = lambda: mock_current_user
    yield
    application.dependency_overrides.clear()


# @pytest.fixture
# def override_uow(uow):
#     application.dependency_overrides[get_unit_of_work] = lambda: uow
#     yield
#     application.dependency_overrides.clear()
