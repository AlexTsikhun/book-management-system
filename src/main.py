from fastapi import Depends, FastAPI
from fastapi_limiter.depends import RateLimiter

from book_management.routers import books
from error_handlers import not_found_error_handler
from exceptions import DoesNotExistError
from lifespan import lifespan

application = FastAPI(
    title="Book Management Application API",
    root_path="/api/v1",
    lifespan=lifespan,
    dependencies=[Depends(RateLimiter(times=5, seconds=60))],
)

application.include_router(books.router)

application.add_exception_handler(DoesNotExistError, not_found_error_handler)
