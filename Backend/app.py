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
    password="AntonellaCedricLucca18",  # Cambiar por tu contraseña segura
    database="mype"
)

#password="ClaveSegura123@"
#password="AntonellaCedricLucca18"

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
        return jsonify({"status": "ok", "mensaje": "Inicio de sesión exitoso", "id_usuario": user["id_usuario"]})
    else:
        return jsonify({"status": "error", "mensaje": "Credenciales incorrectas"}), 401

# Ruta para registrar un nuevo usuario
@app.route('/registro', methods=['POST'])
def registro():
    data = request.get_json()
    nombre= data.get('nombre')
    usuario = data.get('usuario')
    correo = data.get('correo')
    id_rol = data.get('id_rol')
    contrasena = data.get('contrasena')

    # Validar campos
    if not (nombre and usuario and correo and id_rol and contrasena):
        return jsonify({"status": "error", "mensaje": "Todos los campos son obligatorios."}), 400

    # Hash de la contraseña
    hashed_password = bcrypt.hashpw(contrasena.encode('utf-8'), bcrypt.gensalt())

    try:
        cursor = db.cursor()
        query = """
        INSERT INTO usuarios (nombre_completo, nombre_usuario, contraseña_hash, correo, id_rol)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (nombre, usuario, hashed_password.decode('utf-8'), correo, id_rol))
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

@app.route('/productos', methods=['GET'])
def obtener_productos():
    cursor = db.cursor(dictionary=True)
    query = """
        SELECT id_producto, nombre_producto, stock_actual, genero,
               marca, modelo, color, talla, precio_unitario
        FROM productos
    """
    cursor.execute(query)
    productos = cursor.fetchall()
    return jsonify(productos)

@app.route('/ventas', methods=['GET'])
def obtener_ventas():
    cursor = db.cursor(dictionary=True)
    query = """
        SELECT id_producto, nombre_producto, stock_actual, genero,
               marca, modelo, color, talla, precio_unitario
        FROM ventas
    """
    cursor.execute(query)
    productos = cursor.fetchall()
    return jsonify(productos)


@app.route('/movimientos', methods=['POST'])
def registrar_movimiento():
    data = request.get_json()
    productos = data.get('productos')
    id_usuario = data.get('id_usuario', 1)  # Puedes reemplazar esto con una sesión real

    if not productos:
        return jsonify({'status': 'error', 'mensaje': 'No se recibieron productos'}), 400

    try:
        cursor = db.cursor()

        # Insertar movimiento
        cursor.execute("INSERT INTO movimientos (tipo_movimiento, motivo, id_usuario) VALUES (%s, %s, %s)", 
                       ('entrada', 'Ingreso de mercadería', id_usuario))
        id_movimiento = cursor.lastrowid

        # Insertar productos y detalle
        for prod in productos:
            nombre = prod['nombre']
            marca = prod['marca']
            modelo = prod['modelo']
            color = prod['color']
            talla = prod['talla']
            genero = prod['genero']
            precio = float(prod['precio'])
            cantidad = int(prod['cantidad'])

            # Buscar si ya existe
            cursor.execute("""
                SELECT id_producto FROM productos 
                WHERE nombre_producto = %s AND marca = %s AND modelo = %s AND color = %s AND talla = %s AND genero = %s
            """, (nombre, marca, modelo, color, talla, genero))
            result = cursor.fetchone()

            if result:
                id_producto = result[0]
                # Actualizar stock
                cursor.execute("UPDATE productos SET stock_actual = stock_actual + %s WHERE id_producto = %s",
                               (cantidad, id_producto))
            else:
                # Insertar producto
                cursor.execute("""
                    INSERT INTO productos (nombre_producto, marca, modelo, color, talla, genero, precio_unitario, stock_actual)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (nombre, marca, modelo, color, talla, genero, precio, cantidad))
                id_producto = cursor.lastrowid

            # Insertar en detalle
            cursor.execute("""
                INSERT INTO detallemovimiento (id_movimiento, id_producto, cantidad)
                VALUES (%s, %s, %s)
            """, (id_movimiento, id_producto, cantidad))

        db.commit()
        return jsonify({'status': 'ok', 'mensaje': 'Movimiento registrado correctamente'})

    except Exception as e:
        import traceback
        print('Error en movimiento:')
        traceback.print_exc()
        db.rollback()
        return jsonify({'status': 'error', 'mensaje': 'Error al registrar el movimiento'}), 500

print("Rutas disponibles:")
for rule in app.url_map.iter_rules():
    print(f"{rule.methods} - {rule.rule}")

if __name__ == '__main__':
    app.run(port=5000, debug=True)
