from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Permite peticiones desde Electron

# Datos de ejemplo (puedes conectar una BD real después)
usuarios = {
    "admin": "1234",
    "user": "pass"
}

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('usuario')
    password = data.get('contrasena')

    if usuarios.get(username) == password:
        return jsonify({"status": "ok", "mensaje": "Inicio de sesión exitoso"})
    else:
        return jsonify({"status": "error", "mensaje": "Credenciales incorrectas"}), 401

if __name__ == '__main__':
    app.run(port=5000, debug=True)
