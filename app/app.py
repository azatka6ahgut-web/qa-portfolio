from flask import Flask, jsonify, request

app = Flask(__name__)

# База данных в памяти (список заказов)
orders = [
    {"id": 1, "user": "Azat", "amount": 5000, "status": "created"},
    {"id": 2, "user": "Ivan", "amount": 15000, "status": "paid"},
]

# GET /health — проверка что сервис живой
@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

# GET /orders — получить все заказы
@app.route('/orders', methods=['GET'])
def get_orders():
    return jsonify(orders)

# GET /orders/<id> — получить заказ по ID
@app.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    order = next((o for o in orders if o["id"] == order_id), None)
    if not order:
        return jsonify({"error": "Order not found"}), 404
    return jsonify(order)

# POST /orders — создать новый заказ
@app.route('/orders', methods=['POST'])
def create_order():
    data = request.get_json()

    # Валидация — проверяем что нужные поля есть
    if not data:
        return jsonify({"error": "Request body is required"}), 400
    if "user" not in data:
        return jsonify({"error": "Field 'user' is required"}), 400
    if "amount" not in data:
        return jsonify({"error": "Field 'amount' is required"}), 400
    if data["amount"] <= 0:
        return jsonify({"error": "Amount must be greater than 0"}), 400

    new_order = {
        "id": len(orders) + 1,
        "user": data["user"],
        "amount": data["amount"],
        "status": "created"
    }
    orders.append(new_order)
    return jsonify(new_order), 201

# DELETE /orders/<id> — удалить заказ
@app.route('/orders/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    order = next((o for o in orders if o["id"] == order_id), None)
    if not order:
        return jsonify({"error": "Order not found"}), 404
    orders.remove(order)
    return jsonify({"message": f"Order {order_id} deleted"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)