import requests

BASE_URL = "http://localhost:5000"

# Получаем токены один раз для всех тестов
def get_admin_token():
    response = requests.post(f"{BASE_URL}/login", json={
        "username": "admin",
        "password": "password"
    })
    return response.json()["token"]

def get_user_token():
    response = requests.post(f"{BASE_URL}/login", json={
        "username": "user",
        "password": "user123"
    })
    return response.json()["token"]

# Токены на уровне модуля — запрашиваются один раз
ADMIN_TOKEN = None
USER_TOKEN = None

def setup_module(module):
    """Запускается один раз перед всеми тестами"""
    global ADMIN_TOKEN, USER_TOKEN
    ADMIN_TOKEN = get_admin_token()
    USER_TOKEN = get_user_token()

# ===== HEALTH =====

def test_health_check():
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

# ===== GET ORDERS =====

def test_get_all_orders():
    response = requests.get(f"{BASE_URL}/orders")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_order_not_found():
    response = requests.get(f"{BASE_URL}/orders/99999")
    assert response.status_code == 404
    assert "error" in response.json()

# ===== LOGIN =====

def test_login_admin_success():
    assert ADMIN_TOKEN is not None

def test_login_user_success():
    assert USER_TOKEN is not None

def test_login_wrong_password():
    response = requests.post(f"{BASE_URL}/login", json={
        "username": "admin",
        "password": "wrongpassword"
    })
    assert response.status_code == 401

def test_login_missing_fields():
    response = requests.post(f"{BASE_URL}/login", json={
        "username": "admin"
    })
    assert response.status_code == 400

# ===== POST ORDERS =====

def test_create_order_as_admin():
    response = requests.post(f"{BASE_URL}/orders",
        json={"user": "Azat", "amount": 3000},
        headers={"Authorization": f"Bearer {ADMIN_TOKEN}"}
    )
    assert response.status_code == 201
    assert response.json()["status"] == "created"

def test_create_order_as_user_forbidden():
    response = requests.post(f"{BASE_URL}/orders",
        json={"user": "test", "amount": 1000},
        headers={"Authorization": f"Bearer {USER_TOKEN}"}
    )
    assert response.status_code == 403
    assert response.json()["error"] == "Admin access required"

def test_create_order_no_token():
    response = requests.post(f"{BASE_URL}/orders",
        json={"user": "Azat", "amount": 3000}
    )
    assert response.status_code == 401

def test_create_order_no_amount():
    response = requests.post(f"{BASE_URL}/orders",
        json={"user": "Azat"},
        headers={"Authorization": f"Bearer {ADMIN_TOKEN}"}
    )
    assert response.status_code == 400

def test_create_order_negative_amount():
    response = requests.post(f"{BASE_URL}/orders",
        json={"user": "Azat", "amount": -500},
        headers={"Authorization": f"Bearer {ADMIN_TOKEN}"}
    )
    assert response.status_code == 400
    assert response.json()["error"] == "Amount must be greater than 0"

def test_create_order_no_user():
    response = requests.post(f"{BASE_URL}/orders",
        json={"amount": 1000},
        headers={"Authorization": f"Bearer {ADMIN_TOKEN}"}
    )
    assert response.status_code == 400

# ===== DELETE ORDERS =====

def test_delete_order_as_user_forbidden():
    response = requests.delete(f"{BASE_URL}/orders/1",
        headers={"Authorization": f"Bearer {USER_TOKEN}"}
    )
    assert response.status_code == 403

def test_delete_order_not_found():
    response = requests.delete(f"{BASE_URL}/orders/99999",
        headers={"Authorization": f"Bearer {ADMIN_TOKEN}"}
    )
    assert response.status_code == 404

def test_delete_order_no_token():
    response = requests.delete(f"{BASE_URL}/orders/1")
    assert response.status_code == 401