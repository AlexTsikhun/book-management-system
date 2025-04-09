from httpx import AsyncClient


class BaseAPITest:
    async def _create_user(
        self,
        client: AsyncClient,
        username: str = "testuser",
        email: str = "test@example.com",
        password: str = "password123",
    ) -> dict:
        user_data = {"username": username, "email": email, "password": password}
        response = await client.post("/auth/register", json=user_data)
        assert response.status_code == 200, f"Failed to create user: {response.text}"
        return response.json()

    async def _create_book(
        self, client: AsyncClient, title: str = "Test Book", genre: str = "Fiction", year: int = 2023
    ) -> dict:
        book_data = {
            "title": title,
            "author_name": "Test Author",
            "genre": genre,
            "published_year": year,
        }
        response = await client.post("/books/", json=book_data)
        assert response.status_code == 200, f"Failed to create book: {response.text}"
        return response.json()
