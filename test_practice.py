import requests
import pytest
import allure

BASE_URL = "http://localhost:5000"

@pytest.fixture
def my_url():
    return BASE_URL

@pytest.fixture(scope="session")
def admin_token():
    response = requests.post(BASE_URL + "/login", json={
        "username": "admin",
        "password": "password"
    })
    return response.json()["token"]

@allure.feature("Orders API")
def test_create_order(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = requests.post(
        BASE_URL + "/orders",
        headers=headers,
        json={"user": "Azat", "amount": 1000}
    )
    assert response.status_code == 201
    assert "id" in response.json()

@allure.feature("Orders API")
def test_create_order_id1(admin_token):
    # Создаём заказ
    headers = {"Authorization": f"Bearer {admin_token}"}
    response_create = requests.post(
        BASE_URL + "/orders",
        headers=headers,
        json={"user": "Azat", "amount": 1000}
    )
    assert response_create.status_code == 201
    order_id = response_create.json()["id"]

    # Получаем по id
    response_get = requests.get(BASE_URL + f"/orders/{order_id}",
                                headers=headers)
    assert response_get.status_code == 200
    assert response_get.json()["amount"] == 1000
                            
@allure.feature("Orders API")
def test_create_order_no_token():
    response = requests.post(f"{BASE_URL}/orders",
        json={"user": "Azat", "amount": 3000}
    )
    assert response.status_code == 401

@allure.feature("Orders API")
def test_order_with_invalid_token():
    headers={"Authorization": f"Bearer asdasdefe"}
    response = requests.post(f"{BASE_URL}/orders",
                              headers=headers,
        json={"user": "Azat", "amount": 3000}
    )
    
    assert response.status_code == 401



@pytest.mark.parametrize("order_data", [
    {"user":"azat", "amount": 5000},
    {"user":"Johnson" , "amount": 9999},
    {"user":"Jeraxinio" , "amount": 3000}
])

@allure.feature("Orders API")
def test_create_order_parametrized(auth_headers, order_data):
    response = requests.post(f"{BASE_URL}/orders",
                              headers=auth_headers,
                              json=order_data
    )
    assert response.status_code == 201



@pytest.fixture(scope="session")
def user_token():
    """Получаем токен один раз на весь запуск тестов"""
    response = requests.post(BASE_URL + "/login", json={
        "username": "user",
        "password": "user123"
    })
    return response.json()["token"]

@pytest.fixture(scope="session")
def user_auth_headers(user_token):
    """Готовые заголовки с токеном пользователя (не admin)"""
    return {"Authorization": f"Bearer {user_token}"}

@allure.feature("Orders API")
@allure.story("Create Order")
def test_create_order_forbidden_for_user(user_auth_headers):
    response = requests.post(f"{BASE_URL}/orders",
                             headers=user_auth_headers,
                             json={"user": "Azat",
                                   "amount": 5000 })
    assert response.status_code == 403

@pytest.mark.parametrize("order_data_bad", [
    {"amount": 50000},
    {"user": "Azat"},
    {"user": "Azat" , "amount": -5}])

@allure.feature("Orders API")
@allure.story("Create Order")
def test_create_order_bad_body(order_data_bad, auth_headers):
    response = requests.post(f"{BASE_URL}/orders",
                             headers=auth_headers,
                             json=order_data_bad)
    assert response.status_code == 400


@allure.feature("Orders API")
@allure.story("Delete Order")
def test_true_token_but_not_admin(user_auth_headers):
    response = requests.delete(f"{BASE_URL}/orders/5", headers=user_auth_headers)
    assert response.status_code == 403

@allure.feature("Orders API")
@allure.story("Delete Order")
def test_delete_order_not_found(auth_headers):
    response = requests.delete(f"{BASE_URL}/orders/9999",
                               headers=auth_headers)
    assert response.status_code == 404



@allure.feature("Orders API")
@allure.story("Delete Order")
def test_delete_order_success(auth_headers):
    # Шаг 1: создаём заказ
    create_response = requests.post(f"{BASE_URL}/orders", headers=auth_headers, json={"user": "Azat", "amount": 1000})
    order_id = create_response.json()["id"]
    
    # Шаг 2: удаляем этот заказ
    delete_response = requests.delete(f"{BASE_URL}/orders/{order_id}", headers=auth_headers)
    assert delete_response.status_code == 200


@allure.feature("Orders API")
@allure.story("Get Order")
def test_check_order(auth_headers):
    create_response = requests.post(f"{BASE_URL}/orders" ,
                                    headers=auth_headers,
                                    json={"user": "Dima",
                                          "amount": 3000})
    order_id = create_response.json()["id"]
    response = requests.get(f"{BASE_URL}/orders/{order_id}",
                            headers=auth_headers)
    assert response.status_code == 200


@allure.feature("Orders API")
@allure.story("Get Order")
def test_check_order_bad_id(user_auth_headers):
    response = requests.get(f"{BASE_URL}/orders/9999",
                            headers=user_auth_headers)
    assert response.status_code == 404


@allure.feature("Orders API")
@allure.story("Delete Order")   
def test_delete_order(auth_headers):
    create_response = requests.post(f"{BASE_URL}/orders",
                                    headers=auth_headers,
                                    json={"user": "Diana",
                                          "amount": 1000})
    order_id = create_response.json()["id"]

    response = requests.delete(f"{BASE_URL}/orders/{order_id}",
                               headers={})
    assert response.status_code == 401

@allure.feature("Orders API")
@allure.story("Get Order")
def test_get_order_list(auth_headers):
    response = requests.get(f"{BASE_URL}/orders",
                            headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@allure.feature("Orders API")
@allure.story("Get Order")
def test_get_order_forbidden_for_other_user(auth_headers, user_auth_headers):
    create_response = requests.post(f"{BASE_URL}/orders",
                                     headers=auth_headers,
                                     json={"user": "Azat", "amount": 1000})
    
    order_id = create_response.json()["id"]
    
    response = requests.get(f"{BASE_URL}/orders/{order_id}",
                            headers=user_auth_headers)
    assert response.status_code == 403


@allure.feature("Orders API")
@allure.story("Get Order")
def test_admin_get_order_other_user(auth_headers):
    create_response = requests.post(f"{BASE_URL}/orders",
                                    headers=auth_headers,
                                    json={"user": "azat" , 
                                          "amount": 2000})
    
    order_id = create_response.json()["id"]

    response = requests.get(f"{BASE_URL}/orders/{order_id}",
                            headers=auth_headers)
    assert response.status_code == 200


@allure.feature("Orders API")
@allure.story("HealthCheck")
def test_health():
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200 
    assert response.json()["status"] == "ok"
    


        