from flask import Flask, request, jsonify
from auth import authenticate_user, register_user
from database import init_db

app = Flask(__name__)

# Inicializa o banco ao iniciar o app
init_db()

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Usuário e senha são obrigatórios!"}), 400

    register_user(username, password)
    return jsonify({"message": f"Usuário '{username}' registrado com sucesso!"})

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Usuário e senha são obrigatórios!"}), 400

    if authenticate_user(username, password):
        return jsonify({"message": "Autenticado com sucesso!"})

    return jsonify({"error": "Usuário ou senha inválidos!"}), 401

if __name__ == '__main__':
    app.run(debug=True)
