from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from auth.schemas import Token, UserCreate, UserResponse
from auth.use_cases import AuthenticateUserUseCase, RegisterUserUseCase
from dependencies import get_unit_of_work
from exceptions import InvalidUserStateError, ValidationError

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse)
async def register_user(
    user_data: UserCreate,
    uow=Depends(get_unit_of_work),
):
    try:
        use_case = RegisterUserUseCase(uow)
        return await use_case(user_data.model_dump())
    except ValidationError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error))


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    uow=Depends(get_unit_of_work),
):
    try:
        use_case = AuthenticateUserUseCase(uow)
        return await use_case(form_data.username, form_data.password)
    except InvalidUserStateError:
        #  ensure security by not providing info about the account status (that's why I changed the exception text)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
