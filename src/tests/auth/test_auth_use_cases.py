import pytest

from auth.use_cases import AuthenticateUserUseCase, RegisterUserUseCase
from exceptions import DoesNotExistError, ValidationError


@pytest.mark.asyncio
class TestAuthUseCases:
    async def test_register_user(self, uow):
        user_data = {"username": "newuser", "email": "new@example.com", "password": "password123"}
        use_case = RegisterUserUseCase(uow)
        result = await use_case(user_data)
        
        assert result["username"] == "newuser"
        assert result["email"] == "new@example.com"

    async def test_register_duplicate_username(self, uow):
        user_data = {"username": "dupuser", "email": "dup1@example.com", "password": "password123"}
        use_case = RegisterUserUseCase(uow)
        await use_case(user_data)

        with pytest.raises(ValidationError) as exc:
            await use_case({"username": "dupuser", "email": "dup2@example.com", "password": "password123"})
        assert "Username already exists" in str(exc.value)

    async def test_authenticate_user(self, uow):
        user_data = {"username": "authuser", "email": "auth@example.com", "password": "password123"}
        register_use_case = RegisterUserUseCase(uow)
        await register_use_case(user_data)

        auth_use_case = AuthenticateUserUseCase(uow)
        result = await auth_use_case("authuser", "password123")
        assert "access_token" in result
        assert result["token_type"] == "bearer"

    async def test_authenticate_invalid_credentials(self, uow):
        auth_use_case = AuthenticateUserUseCase(uow)
        with pytest.raises(DoesNotExistError):
            await auth_use_case("nonexistent", "wrongpass")
