import requests

BASE_URL = "http://localhost:5000"

# ===== GET тесты =====

def test_health_check():
    """Проверка что сервис живой"""
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_get_all_orders():
    """Получить все заказы"""
    response = requests.get(f"{BASE_URL}/orders")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_order_by_id():
    """Получить заказ по существующему ID"""
    response = requests.get(f"{BASE_URL}/orders/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1

def test_get_order_not_found():
    """Получить заказ по несуществующему ID"""
    response = requests.get(f"{BASE_URL}/orders/999")
    assert response.status_code == 404
    assert "error" in response.json()

# ===== POST тесты =====

def test_create_order():
    """Создать заказ с корректными данными"""
    payload = {"user": "Azat", "amount": 3000}
    response = requests.post(f"{BASE_URL}/orders", json=payload)
    assert response.status_code == 201
    assert response.json()["user"] == "Azat"
    assert response.json()["status"] == "created"

def test_create_order_no_amount():
    """Создать заказ без поля amount"""
    payload = {"user": "Azat"}
    response = requests.post(f"{BASE_URL}/orders", json=payload)
    assert response.status_code == 400
    assert "error" in response.json()

def test_create_order_negative_amount():
    """Создать заказ с отрицательной суммой"""
    payload = {"user": "Azat", "amount": -500}
    response = requests.post(f"{BASE_URL}/orders", json=payload)
    assert response.status_code == 400
    assert response.json()["error"] == "Amount must be greater than 0"

def test_create_order_no_user():
    """Создать заказ без поля user"""
    payload = {"amount": 1000}
    response = requests.post(f"{BASE_URL}/orders", json=payload)
    assert response.status_code == 400
    assert "error" in response.json()

# ===== DELETE тесты =====

def test_delete_order_not_found():
    """Удалить несуществующий заказ"""
    response = requests.delete(f"{BASE_URL}/orders/999")
    assert response.status_code == 404
    assert "error" in response.json()