# Простой тест для новой ветки
import requests

BASE_URL = "http://localhost:5000"

def test_health_load():
    # делаем 10 запросов подряд
    for i in range(10):
        response = requests.get(BASE_URL + "/health")
        assert response.status_code == 200