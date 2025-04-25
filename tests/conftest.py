import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.fixture(scope="function")
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as client:
        yield client

@pytest.fixture(scope="function")
async def auth_headers(async_client):
    # Регистрация пользователя
    await async_client.post("/user/register", json={
        "name": "testuser",
        "email": "ivan@example.com",
        "password": "testpass123"
    })
    
    # Логин
    login_response = await async_client.post("/user/login", json={
        "email": "ivan@example.com",
        "password": "testpass123"
    })
    assert login_response.status_code == 200
    tokens = login_response.json()
    return {"Authorization": f"Bearer {tokens['access_token']}"}