from fastapi import FastAPI

from book_management.routers import books

application = FastAPI(title="Book Management Application API")

application.include_router(books.router)
