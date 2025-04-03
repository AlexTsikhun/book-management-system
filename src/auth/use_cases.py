from datetime import datetime, timedelta, timezone
from typing import Any

from auth.services import create_access_token, get_password_hash, verify_password
from config import settings
from exceptions import DoesNotExistError, ValidationError
from repositories.base import AbstractUnitOfWork


class BaseAuthUseCase:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self.uow = uow


class RegisterUserUseCase(BaseAuthUseCase):
    async def __call__(self, user_data: dict) -> dict:
        async with self.uow:
            existing_user = await self.uow.users.retrieve_by_username(user_data.username)
            if existing_user:
                raise ValidationError("username", "Username already exists")

            existing_email = await self.uow.users.retrieve_by_email(user_data.email)
            if existing_email:
                raise ValidationError("email", "Email already exists")

            hashed_password = get_password_hash(user_data.password)
            return await self.uow.users.create(
                {
                    "username": user_data.username,
                    "email": user_data.email,
                    "hashed_password": hashed_password,
                    "created_at": datetime.now(timezone.utc),
                    "is_active": True,
                }
            )


class AuthenticateUserUseCase(BaseAuthUseCase):
    async def __call__(self, username: str, password: str) -> dict[str, Any]:
        async with self.uow:
            user = await self.uow.users.retrieve_by_username(username)
            if not user or not verify_password(password, user.hashed_password):
                raise DoesNotExistError("Incorrect username or password")

            access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)

            await self.uow.users.update(user.id, {"last_login": datetime.now(timezone.utc)})

            return {"access_token": access_token, "token_type": "bearer"}
