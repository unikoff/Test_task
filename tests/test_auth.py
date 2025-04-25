import pytest

TEST_USER = {
    "name": "testuser",
    "email": "ivan@example.com",
    "password": "testpass123"
}

TASK_DATA = {
    "title": "Написать тест",
    "description": "Тестирование FastAPI с JWT",
    "status": "in_progress",
}

@pytest.mark.asyncio
async def test_register_user(async_client):
    response = await async_client.post("/user/register", json=TEST_USER)
    assert response.status_code in (201, 400)

@pytest.mark.asyncio
async def test_login_user(async_client, auth_headers):
    # Проверка, что токен получен
    assert "Authorization" in auth_headers

@pytest.mark.asyncio
async def test_create_task(async_client, auth_headers):
    response = await async_client.post(
        "/tasks",
        json=TASK_DATA,
        headers=auth_headers  # Явная передача заголовков
    )
    assert response.status_code == 200, response.text
    task = response.json()
    assert task["title"] == TASK_DATA["title"]

@pytest.mark.asyncio
async def test_get_user_tasks(async_client, auth_headers):
    response = await async_client.get(
        "/tasks",
        headers=auth_headers  # Явная передача заголовков
    )
    assert response.status_code == 200, response.text
    tasks = response.json()
    assert isinstance(tasks, list)