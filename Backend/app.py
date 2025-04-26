from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)
CORS(app)  # Permite peticiones desde Electron

# Conexión a la base de datos
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="AntonellaCedricLucca18",
    database="mype"
)

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('usuario')
    password = data.get('contrasena')

    cursor = db.cursor(dictionary=True)
    query = "SELECT * FROM usuarios WHERE nombre_usuario = %s AND contraseña_hash = %s"
    cursor.execute(query, (username, password))
    user = cursor.fetchone()

    if user:
        return jsonify({"status": "ok", "mensaje": "Inicio de sesión exitoso"})
    else:
        return jsonify({"status": "error", "mensaje": "Credenciales incorrectas"}), 401

if __name__ == '__main__':
    app.run(port=5000, debug=True)
