import pytest
from httpx import AsyncClient

from tests.base import BaseAPITest


@pytest.mark.asyncio
class TestAuthAPI(BaseAPITest):
    async def test_register_user_success(
        self,
        client: AsyncClient,
        override_dependencies,
    ):
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "password123",
        }
        response = await client.post("/auth/register", json=user_data)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@example.com"
        assert data["is_active"] is True
        assert "created_at" in data
        assert data["last_login"] is None

    async def test_register_user_duplicate_username(
        self,
        client: AsyncClient,
        override_dependencies,
    ):
        await self._create_user(client, username="dupuser", email="dup1@example.com")
        user_data = {
            "username": "dupuser",
            "email": "dup2@example.com",
            "password": "password123",
        }
        response = await client.post("/auth/register", json=user_data)

        assert response.status_code == 409
        assert "Username already exists" in response.text

    async def test_register_user_duplicate_email(
        self,
        client: AsyncClient,
        override_dependencies,
    ):
        await self._create_user(client, username="user1", email="dup@example.com")
        user_data = {
            "username": "user2",
            "email": "dup@example.com",
            "password": "password123",
        }
        response = await client.post("/auth/register", json=user_data)
        assert response.status_code == 409
        assert "Email already exists" in response.text

    async def test_register_user_short_password(
        self,
        client: AsyncClient,
        override_dependencies,
    ):
        user_data = {
            "username": "shortpass",
            "email": "short@example.com",
            "password": "short",
        }
        response = await client.post("/auth/register", json=user_data)
        assert response.status_code == 422
        assert "Password must be at least 8 characters" in response.text

    async def test_login_success(
        self,
        client: AsyncClient,
        override_dependencies,
    ):
        await self._create_user(client, username="loginuser", email="login@example.com", password="password123")
        form_data = {
            "username": "loginuser",
            "password": "password123",
        }
        response = await client.post("/auth/token", data=form_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_invalid_password(
        self,
        client: AsyncClient,
        override_dependencies,
    ):
        await self._create_user(client, username="loginuser", email="login@example.com", password="password123")
        form_data = {
            "username": "loginuser",
            "password": "wrongpass",
        }
        response = await client.post("/auth/token", data=form_data)
        assert response.status_code == 404
        assert "Incorrect username or password" in response.text

    async def test_login_nonexistent_user(
        self,
        client: AsyncClient,
        override_dependencies,
    ):
        form_data = {
            "username": "nonexistent",
            "password": "password123",
        }
        response = await client.post("/auth/token", data=form_data)
        assert response.status_code == 404
        assert "Incorrect username or password" in response.text

    async def test_login_updates_last_login(self, client: AsyncClient, override_dependencies, uow):
        user = await self._create_user(client, username="loginuser", email="login@example.com", password="password123")
        assert user["last_login"] is None

        form_data = {
            "username": "loginuser",
            "password": "password123",
        }
        response = await client.post("/auth/token", data=form_data)
        assert response.status_code == 200

        async with uow:
            updated_user = await uow.users.retrieve_by_username("loginuser")
            assert updated_user.last_login is not None

    async def test_login_inactive_user(self, client: AsyncClient, override_dependencies, uow):
        await self._create_user(client, username="inactiveuser", email="inactive@example.com", password="password123")

        async with uow:
            user = await uow.users.retrieve_by_username("inactiveuser")
            await uow.users.update(user.id, {"is_active": False})

        form_data = {
            "username": "inactiveuser",
            "password": "password123",
        }
        response = await client.post("/auth/token", data=form_data)
        assert response.status_code == 401
        assert "Incorrect username or password" in response.text
