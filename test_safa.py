import pytest
import requests

BASE_URL = "http://localhost:5000"
@pytest.mark.smoke
@pytest.mark.api
def test_health_status_code(): 
    response = requests.get(BASE_URL+"/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
@pytest.mark.api
def test_order_status_code() :

    response = requests.get(BASE_URL+'/orders')
    assert response.status_code == 200 
@pytest.mark.api
def test_orders_response_structure(): 
    
    response = requests.get(BASE_URL+"/orders")
    body = response.json()
    assert isinstance(body , list)
    assert (len(body)>0)
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

@pytest.mark.parametrize("order_id, expected_status", [
    (1,     200),   # существующий заказ → 200
    (9999,  404),   # несуществующий → 404
    (-1,    404),   # отрицательный → 404
    (0,     404),   # ноль → 404
])
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
@pytest.mark.api
def test_order_not_found_error_message():
    response = requests.get (BASE_URL+f"/orders/99999")
    body = response.json()
    assert response.status_code == 404
    assert "error" in body
    assert body["error"] == "Order not found"
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

@pytest.mark.auth
@pytest.mark.api
@pytest.mark.smoke
def test_login_get_token():
    response = requests.post(BASE_URL+"/login",json={
        "username": "admin" , 
        "password": "password"
    })
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
@pytest.mark.auth
@pytest.mark.api
def test_create_invalid_token():
    headers = {"Authorization": "Bearer INVALID_TOKEN_12345"}
    response = requests.post(BASE_URL + "/orders",
                             headers=headers,
                             json={"user": "Azat", "amount": 5000})
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





    