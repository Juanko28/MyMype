from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from fpdf import FPDF
import os
import io
from reportlab.pdfgen import canvas
from datetime import datetime
import mysql.connector
from datetime import date
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

# Iniciar Sesión
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

# Registando nuevo usuario
@app.route('/registro', methods=['POST'])
def registro():
    data = request.get_json()
    nombre = data.get('nombre')
    usuario = data.get('usuario')
    correo = data.get('correo')
    id_rol = data.get('id_rol')
    contrasena = data.get('contrasena')
    dni = data.get('dni')
    telefono = data.get('telefono')
    direccion = data.get('direccion')
    fecha_nacimiento = data.get('fecha_nacimiento')
    salario = data.get('salario')
    genero = data.get('genero')

    if not all([nombre, usuario, correo, id_rol, contrasena, dni, telefono, direccion, fecha_nacimiento, salario, genero]):
        return jsonify({"status": "error", "mensaje": "Todos los campos son obligatorios."}), 400

    hashed_password = bcrypt.hashpw(contrasena.encode('utf-8'), bcrypt.gensalt())

    try:
        cursor = db.cursor()

        # Insertar en usuarios
        insert_usuario = """
        INSERT INTO usuarios (nombre_completo, nombre_usuario, contraseña_hash, correo, id_rol)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(insert_usuario, (nombre, usuario, hashed_password.decode('utf-8'), correo, id_rol))

        creado_por = data.get('creado_por')
        
        nombre_parts = nombre.split(" ", 1)
        nombre_simple = nombre_parts[0]
        apellido = nombre_parts[1] if len(nombre_parts) > 1 else ""

        
        insert_empleado = """
        INSERT INTO empleados (dn   i, nombre, apellido, correo, telefono, direccion, fecha_nacimiento, salario, genero, id_rol, creado_por)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_empleado, (
            dni, nombre_simple, apellido, correo, telefono,
            direccion, fecha_nacimiento, salario, genero,
            id_rol, creado_por
        ))

        db.commit()
        return jsonify({"status": "ok", "mensaje": "Usuario y empleado registrados exitosamente."})

    except Exception as e:
        print('Error en el registro:', e)
        db.rollback()
        return jsonify({"status": "error", "mensaje": "Error al registrar."}), 500


#Los Roles
@app.route('/roles', methods=['GET'])
def obtener_roles():
    cursor = db.cursor(dictionary=True)
    query = "SELECT id_rol, nombre_rol FROM roles"
    cursor.execute(query)
    roles = cursor.fetchall()
    return jsonify(roles)

@app.route('/tallas/<modelo>', methods=['GET'])
def obtener_tallas(modelo):
    cursor = db.cursor(dictionary=True)
    query = """
        SELECT DISTINCT talla 
        FROM productos 
        WHERE modelo = %s AND stock_actual <> 0
    """
    cursor.execute(query, (modelo,))
    tallas = cursor.fetchall()
    return jsonify(tallas)


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



@app.route('/movimientos', methods=['POST'])
def registrar_movimiento():
    data = request.get_json()
    productos = data.get('productos')
    id_usuario = data.get('id_usuario', 1)  # falra arreglar esto DX

    if not productos:
        return jsonify({'status': 'error', 'mensaje': 'No se recibieron productos'}), 400

    try:
        cursor = db.cursor()

        cursor.execute("INSERT INTO movimientos (tipo_movimiento, motivo, id_usuario) VALUES (%s, %s, %s)", 
                       ('entrada', 'Ingreso de mercadería', id_usuario))
        id_movimiento = cursor.lastrowid
        
        for prod in productos:
            nombre = prod.get('nombre')
            marca = prod.get('marca')
            modelo = prod.get('modelo')
            color = prod.get('color')
            talla = prod.get('talla')
            genero = prod.get('genero')
            precio = float(prod.get('precio', 0))
            cantidad = int(prod.get('cantidad', 0))
        
            cursor.execute("""
                SELECT id_producto FROM productos 
                WHERE nombre_producto = %s AND marca = %s AND modelo = %s AND color = %s AND talla = %s AND genero = %s
            """, (nombre, marca, modelo, color, talla, genero))
            result = cursor.fetchone()

            if result:
                id_producto = result[0] #Actiañzaaaaaaaaaar
                cursor.execute("UPDATE productos SET stock_actual = stock_actual + %s WHERE id_producto = %s",
                               (cantidad, id_producto))
            else: #Insertaaaaaaaaar
                cursor.execute("""  
                    INSERT INTO productos (nombre_producto, marca, modelo, color, talla, genero, precio_unitario, stock_actual)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (nombre, marca, modelo, color, talla, genero, precio, cantidad))
                id_producto = cursor.lastrowid
      
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
    
# Jalar ventas
@app.route('/ventas', methods=['GET'])
def obtener_ventas():
    cursor = db.cursor(dictionary=True)
    query = "SELECT id_venta, fecha_venta, total_con_impuesto FROM ventas ORDER BY fecha_venta DESC"
    cursor.execute(query)
    ventas = cursor.fetchall()
    return jsonify(ventas)

# Detalle de Venta
@app.route('/ventas/<int:id_venta>/detalle', methods=['GET'])
def obtener_detalle_venta(id_venta):
    cursor = db.cursor(dictionary=True)
    query = """
        SELECT 
            p.nombre_producto,
            p.marca,
            p.modelo,
            p.color,
            p.talla,
            p.genero,
            dv.cantidad,
            dv.precio_unitario,
            dv.subtotal
        FROM detalleventa dv
        JOIN productos p ON dv.id_producto = p.id_producto
        WHERE dv.id_venta = %s
    """
    cursor.execute(query, (id_venta,))
    detalle = cursor.fetchall()
    return jsonify(detalle)

@app.route('/ventas', methods=['POST'])
def registrar_venta():
    data = request.get_json()
    productos = data.get('productos')
    id_usuario = data.get('id_usuario')

    if not productos:
        return jsonify({'status': 'error', 'mensaje': 'No se recibieron productos'}), 400

    try:
        cursor = db.cursor()

        subtotal_total = 0.0
        for p in productos:
            subtotal_total += float(p['precio_unitario']) * int(p['cantidad'])

        impuesto = 0.18
        total_con_impuesto = round(subtotal_total * (1 + impuesto), 2)

        cursor.execute("""
            INSERT INTO ventas (id_usuario, total, impuesto_aplicado, total_con_impuesto)
            VALUES (%s, %s, %s, %s)
        """, (id_usuario, subtotal_total, 18.00, total_con_impuesto))
        id_venta = cursor.lastrowid

        for prod in productos:
            modelo = prod['modelo']
            talla = prod['talla']
            cantidad = int(prod['cantidad'])
            precio_unitario = float(prod['precio_unitario'])

            cursor_producto = db.cursor()
            cursor_producto.execute(
                "SELECT id_producto, stock_actual FROM productos WHERE modelo = %s AND talla = %s",
                (modelo, talla)
            )
            result = cursor_producto.fetchone()
            cursor_producto.close()

            if not result:
                db.rollback()
                return jsonify({'status': 'error', 'mensaje': f"Producto con modelo '{modelo}' y talla '{talla}' no encontrado"}), 400

            id_producto, stock_actual = result

            if cantidad > stock_actual:
                db.rollback()
                return jsonify({
                    'status': 'error',
                    'mensaje': f"No hay suficiente stock para el modelo '{modelo}' talla '{talla}'. Disponible: {stock_actual}, solicitado: {cantidad}"
                }), 400

            subtotal = round(precio_unitario * cantidad, 2)

            cursor.execute("""
                INSERT INTO detalleventa (id_venta, id_producto, cantidad, precio_unitario, subtotal)
                VALUES (%s, %s, %s, %s, %s)
            """, (id_venta, id_producto, cantidad, precio_unitario, subtotal))

            cursor.execute("""
                UPDATE productos SET stock_actual = stock_actual - %s WHERE id_producto = %s
            """, (cantidad, id_producto))

        db.commit()
        return jsonify({'status': 'ok', 'mensaje': 'Venta registrada correctamente'}), 201

    except Exception as e:
        import traceback
        traceback.print_exc()
        db.rollback()
        return jsonify({'status': 'error', 'mensaje': 'Error al registrar la venta'}), 500

# Sacando Total VEntas - REPORTE LOGISTICO
@app.route('/api/costoLogis', methods=['GET'])
def obtener_costo_total():
    try:
        cursor = db.cursor()
        cursor.execute("SELECT salario FROM mype.empleados")
        salarios = cursor.fetchall()
        cursor.close()

        total_salarios = sum([float(s[0]) for s in salarios])

        # estaticoos 
        servicio = 15 #diario 
        alquiler = 15 #diario

        costo_total = total_salarios + servicio + alquiler

        return jsonify({
            'costo_total': costo_total
        }), 200

    except Exception as e:
        print(f"Error al obtener el costo total: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/ventas-totales', methods=['GET'])
def obtener_total_ventas_por_fecha():
    try:
        cursor = db.cursor(dictionary=True)
        query = """
            SELECT 
                fecha_venta AS fecha, 
                total 
            FROM mype.ventas
            ORDER BY fecha_venta ASC
        """
        cursor.execute(query)
        resultados = cursor.fetchall()  # <-- se leen todos los resultados
        cursor.close()  # <-- se cierra el cursor

        # Formatear fechas
        for r in resultados:
            if isinstance(r["fecha"], datetime):
                r["fecha"] = r["fecha"].strftime('%Y-%m-%d %H:%M:%S')

        return jsonify(resultados), 200

    except Exception as err:
        print(f"Error al obtener ventas: {err}")
        return jsonify({"error": str(err)}), 500


# Sacando Total VEntas - REPORTE INVENTARIO
@app.route('/api/total-cantidad', methods=['GET'])
def get_total_cantidad():
    try:
        cursor = db.cursor()

        cursor.execute("SELECT IFNULL(SUM(stock_actual), 0) FROM mype.productos")
        total_productos = cursor.fetchone()[0] or 0

        cursor.execute("SELECT IFNULL(SUM(cantidad), 0) FROM mype.detalleventa")
        total_detalleventa = cursor.fetchone()[0] or 0

        cursor.close()

        total = total_productos + total_detalleventa
        return jsonify({'total_cantidad': total}), 200
    except Exception as e:
        print("Error al obtener la cantidad total:", e)
        return jsonify({'error': 'Error interno del servidor al obtener la cantidad total.'}), 500


@app.route('/api/ventas', methods=['GET'])
def obtener_cantidad_ventas():
    try:
        cursor = db.cursor(dictionary=True)

        query = """
            SELECT 
                v.fecha_venta AS fecha,
                dv.cantidad
            FROM mype.detalleventa dv
            JOIN mype.ventas v ON dv.id_venta = v.id_venta
            ORDER BY v.fecha_venta ASC
        """
        cursor.execute(query)
        resultados = cursor.fetchall()

        # Gracias GPT
        for r in resultados:
            if isinstance(r["fecha"], datetime):
                r["fecha"] = r["fecha"].strftime('%Y-%m-%d %H:%M:%S')

        return jsonify(resultados), 200

    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500


                           
print("Rutas disponibles:")
for rule in app.url_map.iter_rules():
    print(f"{rule.methods} - {rule.rule}")

if __name__ == '__main__':
    app.run(port=5000, debug=True)
