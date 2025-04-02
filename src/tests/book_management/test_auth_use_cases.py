import pytest
from auth.schemas import UserCreate
from auth.use_cases import AuthenticateUserUseCase, RegisterUserUseCase
from repositories.fake.containers import FakeUnitOfWork
from exceptions import ValidationError, DoesNotExistError

@pytest.mark.asyncio
async def test_register_user_success():
    uow = FakeUnitOfWork()
    use_case = RegisterUserUseCase(uow)
    user_data = UserCreate(username="testuser", email="test@example.com", password="password123")
    result = await use_case(user_data)
    assert result.email == "test@example.com"
    # assert hasattr(result, "id")

@pytest.mark.asyncio
async def test_register_user_duplicate_username():
    uow = FakeUnitOfWork()
    use_case = RegisterUserUseCase(uow)
    user_data = UserCreate(username="testuser", email="test@example.com", password="password123")
    await use_case(user_data)
    with pytest.raises(ValidationError) as exc:
        await use_case(user_data)

    print(str(exc.value), "55555555555555555")    
    assert "Username already exists" in str(exc.value)

@pytest.mark.asyncio
async def test_login_success():
    uow = FakeUnitOfWork()
    register_use_case = RegisterUserUseCase(uow)
    login_use_case = AuthenticateUserUseCase(uow)
    user_data = UserCreate(username="testuser", email="test@example.com", password="password123")
    await register_use_case(user_data)
    token = await login_use_case("testuser", "password123")
    assert "access_token" in token
    assert token["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_invalid_credentials():
    uow = FakeUnitOfWork()
    login_use_case = AuthenticateUserUseCase(uow)
    with pytest.raises(DoesNotExistError) as exc:
        await login_use_case("testuser", "wrongpassword")
    assert "Incorrect username or password" in str(exc.value)
