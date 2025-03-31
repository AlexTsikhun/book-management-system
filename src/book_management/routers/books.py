from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from book_management.schemas.books import BookCreateSchema, BookResponseSchema
from book_management.use_cases.books import CreateBookUseCase, RetrieveBooksUseCase
from dependencies import get_unit_of_work

router = APIRouter(prefix="/books", tags=["books"])


@router.get("/", response_model=list[BookResponseSchema])
async def retrieve_books(
    request: Request,
    page: int = 1,
    per_page: int = 10,
    sort_by: str = "title",
    uow=Depends(get_unit_of_work),
):
    use_case = RetrieveBooksUseCase(uow)
    books_data = await use_case(page=page, per_page=per_page, sort_by=sort_by)
    return JSONResponse(content=books_data)


@router.post("/", response_model=BookResponseSchema)
async def create_book(
    request: Request,
    book_data: BookCreateSchema,
    uow=Depends(get_unit_of_work),
):
    use_case = CreateBookUseCase(uow)
    created_book = await use_case(book_data.model_dump())
    return JSONResponse(content=created_book)
