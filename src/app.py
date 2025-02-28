from flask import Flask, request, jsonify
from pyd6.pyd6 import simulate_attack

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/simulate_attack', methods=['POST'])
def attack():
    data = request.json
    attacker_name = data.get('attacker')
    defender_name = data.get('defender')

    result = simulate_attack(attacker_name, defender_name)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)