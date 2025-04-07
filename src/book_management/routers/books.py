import io

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from pydantic import ValidationError as PydanticValidationError

from auth.schemas import UserResponse
from book_management.schemas.books import BookBulkImportResponse, BookCreateSchema, BookResponseSchema
from book_management.services.books import FileParserFactory
from book_management.use_cases.books import (
    BulkImportBooksUseCase,
    CreateBookUseCase,
    DeleteBookUseCase,
    ExportBooksUseCase,
    RecommendBooksUseCase,
    RetrieveBooksUseCase,
    RetrieveBookUseCase,
    UpdateBookUseCase,
)
from dependencies import get_current_user, get_unit_of_work
from exceptions import ValidationError

router = APIRouter(prefix="/books", tags=["books"])


@router.get("/export")
async def export_books(
    format: str = "json",
    uow=Depends(get_unit_of_work),
    current_user: UserResponse = Depends(get_current_user),
):
    format_lower = format.lower()
    if format_lower not in ["json", "csv"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Format must be 'json' or 'csv'")

    use_case = ExportBooksUseCase(uow)
    file_content = await use_case(format=format_lower)

    media_type = "application/json" if format_lower == "json" else "text/csv"
    file_extension = "json" if format_lower == "json" else "csv"

    return StreamingResponse(
        io.StringIO(file_content),
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename=books_export.{file_extension}"},
    )


@router.get("/", response_model=list[BookResponseSchema])
async def retrieve_books(
    page: int = 1,
    per_page: int = 10,
    sort_by: str = "title:asc",
    uow=Depends(get_unit_of_work),
):
    use_case = RetrieveBooksUseCase(uow)
    return await use_case(page=page, per_page=per_page, sort_by=sort_by)


@router.post("/", response_model=BookResponseSchema)
async def create_book(
    book_data: BookCreateSchema,
    uow=Depends(get_unit_of_work),
    current_user: UserResponse = Depends(get_current_user),
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
    current_user: UserResponse = Depends(get_current_user),
):
    use_case = UpdateBookUseCase(uow)
    return await use_case(book_id, book_data.model_dump())


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_id: int,
    uow=Depends(get_unit_of_work),
    current_user: UserResponse = Depends(get_current_user),
):
    use_case = DeleteBookUseCase(uow)
    return await use_case(book_id)


@router.post("/bulk-import", response_model=BookBulkImportResponse)
async def bulk_import_books(
    file: UploadFile = File(...),
    uow=Depends(get_unit_of_work),
    current_user: UserResponse = Depends(get_current_user),
):
    if file.content_type not in ["text/csv", "application/json"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Please ensure the file is in JSON or CSV format."
        )

    content = await file.read()
    file_content = content.decode()

    parser = FileParserFactory.get_parser(file.filename)
    try:
        books_data = parser.parse(file_content)
    except ValueError as error:
        raise ValidationError("file", f"File parsing error: {str(error)}")
    except TypeError:
        raise ValidationError("file", "Missing required field")

    valid_books = []
    failed_info = []
    for book_data in books_data:
        try:
            book = BookCreateSchema(**book_data)
            valid_books.append(book.model_dump())
        except PydanticValidationError as error:
            failed_info.append({"data": book_data, "error": str(error)})

    use_case = BulkImportBooksUseCase(uow)
    result = await use_case(valid_books)

    return {
        "total_items": len(books_data),
        "successful": result["successful"],
        "failed": len(failed_info),
        "failed_info": failed_info,
    }


@router.get("/recommendations/{book_id}", response_model=list[BookResponseSchema])
async def recommend_books(
    book_id: int,
    limit: int = 5,
    uow=Depends(get_unit_of_work),
    current_user: UserResponse = Depends(get_current_user),
):
    use_case = RecommendBooksUseCase(uow)
    return await use_case(book_id=book_id, limit=limit)
