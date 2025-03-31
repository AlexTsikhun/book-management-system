from repositories.postgres.container import PostgresUnitOfWork


def get_unit_of_work() -> PostgresUnitOfWork():
    return PostgresUnitOfWork()
