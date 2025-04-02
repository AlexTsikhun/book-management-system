from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, field_validator

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

    @field_validator('password')
    def validate_password(cls, password: str):
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters")
        return password

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    last_login: datetime | None

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None
    