from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from book_management.schemas.books import BookCreateSchema, BookResponseSchema
from book_management.use_cases.books import (
    CreateBookUseCase,
    DeleteBookUseCase,
    RetrieveBooksUseCase,
    RetrieveBookUseCase,
    UpdateBookUseCase,
)
from dependencies import get_unit_of_work

router = APIRouter(prefix="/books", tags=["books"])


@router.get("/", response_model=list[BookResponseSchema])
async def retrieve_books(
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
    book_data: BookCreateSchema,
    uow=Depends(get_unit_of_work),
):
    use_case = CreateBookUseCase(uow)
    return await use_case(book_data.model_dump())


@router.get("/{book_id}", response_model=BookResponseSchema)
async def retrieve_book(
    book_id: int,
    uow=Depends(get_unit_of_work),
):
    use_case = RetrieveBookUseCase(uow)
    return await use_case(book_id)


@router.put("/{book_id}", response_model=BookResponseSchema)
async def update_book(
    book_id: int,
    book_data: BookResponseSchema,
    uow=Depends(get_unit_of_work),
):
    use_case = UpdateBookUseCase(uow)
    return await use_case(book_id, book_data.model_dump())


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_id: int,
    uow=Depends(get_unit_of_work),
):
    use_case = DeleteBookUseCase(uow)
    return await use_case(book_id)
