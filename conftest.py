import pytest
import requests

BASE_URL = "http://localhost:5000"

@pytest.fixture
def orders_response():
    response = requests.get(BASE_URL + "/orders")
    return response

@pytest.fixture(scope="session")
def admin_token():
    """Получаем токен один раз на весь запуск тестов"""
    response = requests.post(BASE_URL + "/login", json={
        "username": "admin",
        "password": "password"
    })
    return response.json()["token"]


@pytest.fixture(scope="session")
def auth_headers(admin_token):
    """Готовые заголовки с токеном"""
    return {"Authorization": f"Bearer {admin_token}"}