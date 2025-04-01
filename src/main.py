from fastapi import FastAPI

from book_management.routers import books
from error_handlers import not_found_error_handler
from exceptions import DoesNotExistError

application = FastAPI(title="Book Management Application API", root_path="/api/v1")

application.include_router(books.router)

application.add_exception_handler(DoesNotExistError, not_found_error_handler)
