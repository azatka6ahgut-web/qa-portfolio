from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

@app.route('/order', methods=['GET'])
def get_order():
    return jsonify({
        "id": 1,
        "user": "Azat",
        "amount": 5000,
        "status": "created"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)