import os
import psycopg2
from flask import Flask, jsonify, request

app = Flask(__name__)

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

# GET /health
@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

# GET /orders
@app.route('/orders', methods=['GET'])
def get_orders():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, username, amount, status FROM orders")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    orders = [{"id": r[0], "user": r[1], "amount": r[2], "status": r[3]} for r in rows]
    return jsonify(orders)

# GET /orders/<id>
@app.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, username, amount, status FROM orders WHERE id = %s", (order_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if not row:
        return jsonify({"error": "Order not found"}), 404
    return jsonify({"id": row[0], "user": row[1], "amount": row[2], "status": row[3]})

# POST /orders
@app.route('/orders', methods=['POST'])
def create_order():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required"}), 400
    if "user" not in data:
        return jsonify({"error": "Field 'user' is required"}), 400
    if "amount" not in data:
        return jsonify({"error": "Field 'amount' is required"}), 400
    if data["amount"] <= 0:
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
    return jsonify({"id": row[0], "user": row[1], "amount": row[2], "status": row[3]}), 201

# DELETE /orders/<id>
@app.route('/orders/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id FROM orders WHERE id = %s", (order_id,))
    if not cur.fetchone():
        cur.close()
        conn.close()
        return jsonify({"error": "Order not found"}), 404
    cur.execute("DELETE FROM orders WHERE id = %s", (order_id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": f"Order {order_id} deleted"}), 200

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)