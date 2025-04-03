from fastapi import Depends, FastAPI
from fastapi_limiter.depends import RateLimiter

import auth.routers as auth
from book_management.routers import books
from error_handlers import invalid_sort_parameter_handler, not_found_error_handler, validation_error_handler
from exceptions import DoesNotExistError, InvalidSortParameterError, ValidationError
from lifespan import lifespan

application = FastAPI(
    title="Book Management Application API",
    root_path="/api/v1",
    lifespan=lifespan,
    dependencies=[Depends(RateLimiter(times=5, seconds=60))],
)

application.include_router(books.router)
application.include_router(auth.router)

application.add_exception_handler(DoesNotExistError, not_found_error_handler)
application.add_exception_handler(ValidationError, validation_error_handler)
application.add_exception_handler(InvalidSortParameterError, invalid_sort_parameter_handler)
