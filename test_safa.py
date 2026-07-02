import psycopg2
import os

from pydantic import BaseModel
from typing import Optional

class OrderSchema(BaseModel):
    id: int
    user: str
    amount: int
    status: str


class LoginSchema(BaseModel):
    token: str

import pytest
import requests
import allure




BASE_URL = "http://localhost:5000"
@allure.feature("Health")
@allure.story("API доступен")
@pytest.mark.smoke
@pytest.mark.api
def test_health_status_code():
    with allure.step("GET /health"):
        response = requests.get(BASE_URL + "/health")
    with allure.step("Проверяем статус 200 и status=ok"):
        assert response.status_code == 200
        assert response.json()["status"] == "ok"



@allure.feature("Orders")
@allure.story("Получение списка заказов")
@pytest.mark.api
def test_order_status_code():
    with allure.step("GET /orders"):
        response = requests.get(BASE_URL + '/orders')
    with allure.step("Статус 200"):
        assert response.status_code == 200


@allure.feature("Orders")
@allure.story("Структура ответа")
@pytest.mark.api
def test_orders_response_structure():
    with allure.step("GET /orders"):
        response = requests.get(BASE_URL + "/orders")
    with allure.step("Проверяем поля"):
        body = response.json()
        assert "id" in body[0]
        assert "status" in body[0]
        assert "amount" in body[0]
        assert "user" in body[0]


@pytest.mark.api
def test_orders_data_types() :
    response = requests.get(BASE_URL+"/orders")
    body = response.json()
    assert isinstance(body , list)
    assert (len(body)>0)
    assert isinstance(body[0]["id"], int)
    assert isinstance(body[0]["status"], str)
    assert isinstance(body[0]["amount"], int)
    assert isinstance(body[0]["user"], str)



@pytest.mark.api
@pytest.mark.smoke
def test_orders_uses_fixture(orders_response):
    assert orders_response.status_code == 200
    body = orders_response.json()
    assert isinstance(body, list)
@pytest.mark.api
def test_order_not_found():
    response = requests.get(BASE_URL+"/orders/99990")
    assert response.status_code == 404


    
@pytest.mark.parametrize("order_id", [9999, 8888, 0 ,-1])
@pytest.mark.api
def test_order_not_found_parametrize(order_id):
    response = requests.get(BASE_URL+f"/orders/{order_id}")
    assert response.status_code == 404



@pytest.mark.smoke
@pytest.mark.api
def test_order_by_id_smoke(auth_headers):
    # Сначала создаём заказ
    create = requests.post(BASE_URL + "/orders",
                          headers=auth_headers,
                          json={"user": "Azat", "amount": 100})
    order_id = create.json()["id"]
    
    # Потом проверяем его
    response = requests.get(BASE_URL + f"/orders/{order_id}")
    assert response.status_code == 200


@allure.feature("Orders")
@allure.story("Заказ не найден")
@pytest.mark.api
def test_order_not_found():
    with allure.step("GET несуществующего заказа"):
        response = requests.get(BASE_URL + "/orders/99990")
    with allure.step("Ожидаем 404"):
        assert response.status_code == 404



@pytest.mark.api
def test_get_singlde_order():
    response = requests.get(BASE_URL+f"/orders/1")
    body = response.json()
    assert response.status_code == 200
    assert body["user"] is not None
    assert "id" in body
    assert "status" in body
    assert "amount" in body
    assert "user" in body
    assert isinstance(body["id"] ,int)
    assert isinstance(body["status"],str)
    assert isinstance(body["amount"],int)
    assert isinstance(body["user"],str)
    assert body["user"] != ""



@allure.feature("Auth")
@allure.story("Логин")
@pytest.mark.auth
@pytest.mark.smoke
def test_login_get_token():
    with allure.step("POST /login"):
        response = requests.post(BASE_URL + "/login",
                    json={"username": "admin", "password": "password"})
    with allure.step("Токен в ответе"):
        assert response.status_code == 200
        assert "token" in response.json()



@pytest.mark.auth
@pytest.mark.api
def test_create_order(auth_headers):
    response = requests.post(BASE_URL+"/orders",
                          headers=auth_headers,
                          json={"user": "Azat" , "amount": 5000})
    assert response.status_code == 201
    assert "id" in response.json()


@allure.feature("Auth")
@allure.story("Невалидный токен")
@pytest.mark.auth
def test_create_invalid_token():
    with allure.step("POST с невалидным токеном"):
        headers = {"Authorization": "Bearer INVALID_TOKEN_12345"}
        response = requests.post(BASE_URL + "/orders",
                     headers=headers,
                     json={"user": "Azat", "amount": 5000})
    with allure.step("Ожидаем 401"):
        assert response.status_code == 401


@pytest.mark.auth
@pytest.mark.api
def test_create_without_token():
    headers = {"Autorization": ""}
    response = requests.post(BASE_URL+"/orders",
                             headers=headers ,
                             json={"user": "Azat", "amount": 5000})
    assert response.status_code == 401
    

@pytest.mark.auth
@pytest.mark.api
def test_create_empty_body(auth_headers):
    response = requests.post(BASE_URL + "/orders",
                             headers=auth_headers,
                             json={})
    assert response.status_code == 400

@pytest.mark.auth
@pytest.mark.api
def test_delete_order(auth_headers):
    create_response = requests.post(BASE_URL+"/orders",
                                    headers=auth_headers,
                                    json={"user": "Azat" , "amount": 1000})
    order_id = create_response.json()["id"]
    delete_response = requests.delete(BASE_URL+f"/orders/{order_id}",
                                      headers=auth_headers)
    assert delete_response.status_code == 200



def test_get_single_order():
    response = requests.get(BASE_URL + "/orders/1")
    assert response.status_code == 200
    OrderSchema(**response.json())  # Pydantic сам проверит все поля и типы


def test_orders_data_types():
    response = requests.get(BASE_URL + "/orders")
    body = response.json()
    assert isinstance(body, list)
    for order in body:
        OrderSchema(**order)  # валидируем каждый объект



@allure.feature("Orders")
@allure.story("Создание заказа")
@pytest.mark.auth
@pytest.mark.api
def test_create_order(auth_headers):
    with allure.step("POST /orders"):
        response = requests.post(BASE_URL + "/orders",
                      headers=auth_headers,
                      json={"user": "Azat", "amount": 5000})
    with allure.step("Проверяем 201 и наличие id"):
        assert response.status_code == 201
        assert "id" in response.json()


@pytest.mark.api
def test_order_saved_in_db(auth_headers):
    # ШАГ 1 — создаём заказ через API
    response = requests.post(
        BASE_URL + "/orders",
        headers=auth_headers,
        json={"user": "Azat", "amount": 9999}
    )
    assert response.status_code == 201
    order_id = response.json()["id"]

    # ШАГ 2 — подключаемся к БД и проверяем
    conn = psycopg2.connect(
        "postgresql://admin:password@localhost:5432/orders_db"
    )
    cursor = conn.cursor()
    
    # ищем заказ в БД по id
    cursor.execute(
        "SELECT id, user, amount, status FROM orders WHERE id = %s",
        (order_id,)
    )
    order = cursor.fetchone()
    conn.close()

    # ШАГ 3 — проверяем что данные правильные
    assert order is not None           # заказ существует в БД
    assert order[2] == 9999            # amount правильный
    assert order[3] == "created"       # статус правильный

    