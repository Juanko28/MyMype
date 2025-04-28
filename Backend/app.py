from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import bcrypt

app = Flask(__name__)
CORS(app)  # Permite peticiones desde Electron

# Conexión a la base de datos
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="ClaveSegura123@",  # Cambiar por tu contraseña segura
    database="mype"
)

# Ruta para iniciar sesión
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('usuario')
    password = data.get('contrasena')

    cursor = db.cursor(dictionary=True)
    query = "SELECT * FROM usuarios WHERE nombre_usuario = %s"
    cursor.execute(query, (username,))
    user = cursor.fetchone()

    if user and bcrypt.checkpw(password.encode('utf-8'), user['contraseña_hash'].encode('utf-8')):
        return jsonify({"status": "ok", "mensaje": "Inicio de sesión exitoso"})
    else:
        return jsonify({"status": "error", "mensaje": "Credenciales incorrectas"}), 401

# Ruta para registrar un nuevo usuario
# Ruta para registrar un nuevo usuario
@app.route('/registro', methods=['POST'])
def registro():
    data = request.get_json()
    usuario = data.get('usuario')
    correo = data.get('correo')
    id_rol = data.get('id_rol')
    contrasena = data.get('contrasena')

    # Validar campos
    if not (usuario and correo and id_rol and contrasena):
        return jsonify({"status": "error", "mensaje": "Todos los campos son obligatorios."}), 400

    # Hash de la contraseña
    hashed_password = bcrypt.hashpw(contrasena.encode('utf-8'), bcrypt.gensalt())

    try:
        cursor = db.cursor()
        query = """
        INSERT INTO usuarios (nombre_usuario, contraseña_hash, correo, id_rol)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (usuario, hashed_password.decode('utf-8'), correo, id_rol))
        db.commit()
        return jsonify({"status": "ok", "mensaje": "Usuario registrado exitosamente."})
    except Exception as e:
        print('Error:', e)
        return jsonify({"status": "error", "mensaje": "Error al registrar el usuario."}), 500


# Ruta para obtener los roles
@app.route('/roles', methods=['GET'])
def obtener_roles():
    cursor = db.cursor(dictionary=True)
    query = "SELECT id_rol, nombre_rol FROM roles"
    cursor.execute(query)
    roles = cursor.fetchall()
    return jsonify(roles)

if __name__ == '__main__':
    app.run(port=5000, debug=True)
