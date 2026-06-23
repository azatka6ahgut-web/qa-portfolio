import os
import logging
import jwt
import psycopg2
from flasgger import Swagger

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/apispec.json",
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/swagger"
}

swagger_template = {
    "info": {
        "title": "QA Portfolio API",
        "description": "REST API для портфолио QA инженера",
        "version": "1.0.0"
    },
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header"
        }
    }
}
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask import Flask, jsonify, request
from functools import wraps

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
swagger = Swagger(app, config=swagger_config, template=swagger_template)
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per minute"]
)
SECRET_KEY = "qa-portfolio-secret"
USERS = {
    "admin": {"password": "password", "role": "admin"},
    "user":  {"password": "user123",  "role": "user"}
}

def get_db():
    return psycopg2.connect(os.environ.get("DATABASE_URL"))

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            username VARCHAR(100) NOT NULL,
            amount INTEGER NOT NULL,
            status VARCHAR(50) DEFAULT 'created'
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            logger.warning("Request without token")
            return jsonify({"error": "Token is missing"}), 401
        try:
            token = token.replace("Bearer ", "")
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            request.current_user = payload
        except jwt.ExpiredSignatureError:
            logger.warning("Expired token")
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            logger.warning("Invalid token")
            return jsonify({"error": "Invalid token"}), 401
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"error": "Token is missing"}), 401
        try:
            token = token.replace("Bearer ", "")
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            if payload.get("role") != "admin":
                logger.warning(f"Access denied — user:{payload.get('user')} role:{payload.get('role')}")
                return jsonify({"error": "Admin access required"}), 403
            request.current_user = payload
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        return f(*args, **kwargs)
    return decorated

@app.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    """
    Получить JWT токен
    ---
    parameters:
      - in: body
        name: body
        required: true
        schema:
          properties:
            username:
              type: string
              example: admin
            password:
              type: string
              example: password
    responses:
      200:
        description: Токен выдан
      401:
        description: Неверные credentials
      400:
        description: Не переданы username/password
    """
    data = request.get_json()
    if not data or "username" not in data or "password" not in data:
        logger.warning("Login failed — missing credentials")
        return jsonify({"error": "Username and password required"}), 400
    
    username = data["username"]
    password = data["password"]
    
    if username not in USERS or USERS[username]["password"] != password:
        logger.warning(f"Login failed — invalid credentials for: {username}")
        return jsonify({"error": "Invalid credentials"}), 401
    
    role = USERS[username]["role"]
    token = jwt.encode(
        {"user": username, "role": role},
        SECRET_KEY,
        algorithm="HS256"
    )
    logger.info(f"Login success — user: {username} role: {role}")
    return jsonify({"token": token, "role": role})

@app.route('/health', methods=['GET'])
def health():
    """
    Проверка работоспособности сервиса
    ---
    responses:
      200:
        description: Сервис работает
        examples:
          application/json: {"status": "ok"}
    """
    logger.info("Health check")
    return jsonify({"status": "ok"})

@app.route('/orders', methods=['GET'])
def get_orders():
    """
    Получить все заказы
    ---
    responses:
      200:
        description: Список заказов
    """
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, username, amount, status FROM orders")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    logger.info(f"GET /orders — returned {len(rows)} orders")
    orders = [{"id": r[0], "user": r[1], "amount": r[2], "status": r[3]} for r in rows]
    return jsonify(orders)

@app.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    """
    Получить заказ по ID
    ---
    parameters:
      - in: path
        name: order_id
        type: integer
        required: true
    responses:
      200:
        description: Заказ найден
      404:
        description: Заказ не найден
    """
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, username, amount, status FROM orders WHERE id = %s", (order_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if not row:
        logger.warning(f"GET /orders/{order_id} — not found")
        return jsonify({"error": "Order not found"}), 404
    logger.info(f"GET /orders/{order_id} — found")
    return jsonify({"id": row[0], "user": row[1], "amount": row[2], "status": row[3]})

@app.route('/orders', methods=['POST'])
@admin_required
def create_order():
    """
    Создать заказ (только admin)
    ---
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          properties:
            user:
              type: string
              example: Azat
            amount:
              type: integer
              example: 5000
    responses:
      201:
        description: Заказ создан
      400:
        description: Ошибка валидации
      401:
        description: Нет токена
      403:
        description: Нет прав
    """
    data = request.get_json()
    if not data:
        logger.warning("POST /orders — empty body")
        return jsonify({"error": "Request body is required"}), 400
    if "user" not in data:
        logger.warning("POST /orders — missing field: user")
        return jsonify({"error": "Field 'user' is required"}), 400
    if "amount" not in data:
        logger.warning("POST /orders — missing field: amount")
        return jsonify({"error": "Field 'amount' is required"}), 400
    if data["amount"] <= 0:
        logger.warning(f"POST /orders — invalid amount: {data['amount']}")
        return jsonify({"error": "Amount must be greater than 0"}), 400
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO orders (username, amount) VALUES (%s, %s) RETURNING id, username, amount, status",
        (data["user"], data["amount"])
    )
    row = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    logger.info(f"POST /orders — created order id:{row[0]} user:{row[1]} amount:{row[2]}")
    return jsonify({"id": row[0], "user": row[1], "amount": row[2], "status": row[3]}), 201

@app.route('/orders/<int:order_id>', methods=['DELETE'])
@admin_required
def delete_order(order_id):
    """
    Удалить заказ (только admin)
    ---
    security:
      - Bearer: []
    parameters:
      - in: path
        name: order_id
        type: integer
        required: true
    responses:
      200:
        description: Заказ удалён
      404:
        description: Заказ не найден
      403:
        description: Нет прав
    """
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id FROM orders WHERE id = %s", (order_id,))
    if not cur.fetchone():
        cur.close()
        conn.close()
        logger.warning(f"DELETE /orders/{order_id} — not found")
        return jsonify({"error": "Order not found"}), 404
    cur.execute("DELETE FROM orders WHERE id = %s", (order_id,))
    conn.commit()
    cur.close()
    conn.close()
    logger.info(f"DELETE /orders/{order_id} — deleted")
    return jsonify({"message": f"Order {order_id} deleted"}), 200

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)