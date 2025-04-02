import os
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from auth.schemas import UserResponse
from auth.services import get_active_current_user, oauth2_scheme

def get_unit_of_work():
    if os.getenv("ENV") == "test":
        from repositories.fake.containers import FakeUnitOfWork

        return FakeUnitOfWork()
    
    from repositories.postgres.container import PostgresUnitOfWork

    return PostgresUnitOfWork()


async def get_current_user(token: str = Depends(oauth2_scheme), uow=Depends(get_unit_of_work)):
    return await get_active_current_user(token, uow)
