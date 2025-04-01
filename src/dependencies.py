import os


def get_unit_of_work():
    if os.getenv("ENV") == "test":
        from repositories.fake.containers import FakeUnitOfWork

        return FakeUnitOfWork()
    else:
        from repositories.postgres.container import PostgresUnitOfWork

        return PostgresUnitOfWork()
