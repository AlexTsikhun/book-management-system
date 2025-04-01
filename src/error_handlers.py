from fastapi import Request, status
from fastapi.responses import JSONResponse

from exceptions import DoesNotExistError


async def not_found_error_handler(request: Request, exception: DoesNotExistError):
    return JSONResponse(
        content={"detail": str(exception.detail)},
        status_code=status.HTTP_404_NOT_FOUND,
    )
