from src.book_management.models import Author, Book
from src.repositories.postgres.repository import PostgresRepository


class BooksRepository(PostgresRepository):
    model_class = Book


class AuthorsRepository(PostgresRepository):
    model_class = Author
