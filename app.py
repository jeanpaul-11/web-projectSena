from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from database import DatabaseManager
from email_service import EmailService
import random
import string
import sqlite3
from flask_cors import CORS
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

app = Flask(__name__)
app.secret_key = '123'  # Añade una clave secreta segura en producción
CORS(app, supports_credentials=True)
db_manager = DatabaseManager()
email_service = EmailService()

@app.route('/')
def index():
    return render_template('index.html', title='Index')

@app.route('/login')
def login():
    return render_template('login.html', title='Login')

@app.route('/olvidar-contrasena')
def olvidar_contrasena():
    return render_template('olvidar-contasena.html', title='Forgot password')

@app.route('/registrarse')
def registrarse():
    return render_template('registrarse.html', title='Sing up')

@app.route('/clientes')
@login_required
def clientes():
    return render_template('clientes.html', title='Clientes')

@app.route('/empleado')
def empleado():
    # Obtener estadísticas para el panel del empleado
    reservas = db_manager.get_reservation_stats()
    menu = db_manager.get_menu_stats()
    mesas = db_manager.get_mesa_stats()
    return render_template('empleado.html', title='Panel de Empleado', reservas=reservas, menu=menu, mesas=mesas)

@app.route('/admin')
def admin():
    # Obtener todas las estadísticas para el panel de administración
    usuarios = db_manager.get_user_stats()
    reservas = db_manager.get_reservation_stats()
    menu = db_manager.get_menu_stats()
    mesas = db_manager.get_mesa_stats()
    return render_template('admin.html', title='Panel de Administrador', usuarios=usuarios, reservas=reservas, menu=menu, mesas=mesas)

@app.route('/reservas')
@login_required
def reservas():
    connection = db_manager.get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM alimentos WHERE estado = 'disponible'")
    platos = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('reservas.html', title='Reservas', platos=platos)

@app.route('/api/sendCredentialsAccess', methods=['POST'])
def api_endpoint():
    data = request.json
    correo = data.get('correo')
    clave = data.get('clave')

    resultado = db_manager.validar_usuario(correo, clave)
    print(f"Correo: {correo}, Clave: {clave}")
    
    if resultado["status"] == "success":
        session['user_id'] = resultado["data"]["id"]
        
    return jsonify(resultado)

@app.route('/api/registro', methods=['POST'])
def registro():
    data = request.json
    resultado = db_manager.insertar_usuario(
        nombres=data.get('nombres'),
        apellidos=data.get('apellidos'),
        tipo_documento=data.get('tipo_documento'),
        num_documento=data.get('num_documento'),
        celular=data.get('celular'),
        email=data.get('email'),
        password=data.get('password')
    )
    
    if resultado["status"] == "success":
        # Enviar correo de bienvenida
        email_service.enviar_correo_bienvenida(
            destinatario=data.get('email'),
            nombre=data.get('nombres')
        )
    
    return jsonify(resultado)

@app.route('/recuperar-clave', methods=['POST'])
def recuperar_clave():
    data = request.json
    email = data.get('email')

    # Verificar si el email existe en la base de datos
    connection = db_manager.get_connection()
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    query = "SELECT * FROM usuarios WHERE correo = ?"
    cursor.execute(query, (email,))
    usuario = cursor.fetchone()

    if not usuario:
        cursor.close()
        connection.close()
        return jsonify({
            "status": "error",
            "message": "No existe una cuenta con este correo electrónico"
        })

    # Generar token aleatorio
    token = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

    # Guardar el token en la base de datos y usarlo como contraseña temporal
    update_query = "UPDATE usuarios SET token_recuperacion = ?, contrasena = ?, estado = 'recuperacion', intentos_fallidos = 0 WHERE correo = ?"
    cursor.execute(update_query, (token, token, email))
    connection.commit()
    cursor.close()
    connection.close()

    # Enviar correo
    resultado = email_service.enviar_correo_recuperacion(email, token)
    
    if resultado["status"] == "success":
        return jsonify({
            "status": "success",
            "message": "Se ha enviado un correo con las instrucciones"
        })
    else:
        return jsonify({
            "status": "error",
            "message": "Error al enviar el correo de recuperación"
        })

@app.route('/api/reservas', methods=['POST'])
def crear_reserva():
    if 'user_id' not in session:
        return jsonify({'error': 'Debe iniciar sesión para hacer una reserva'}), 401

    try:
        data = request.json
        cliente_id = session['user_id']
        fecha = data.get('fecha')
        hora = data.get('hora')
        num_personas = data.get('num_personas')
        platos = data.get('platos', [])

        if not all([fecha, hora, num_personas]):
            return jsonify({'error': 'Faltan datos requeridos'}), 400

        db = DatabaseManager()
        success, message = db.crear_reserva(cliente_id, fecha, hora, num_personas, platos)

        if success:
            return jsonify({'message': message}), 200
        else:
            return jsonify({'error': message}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/usuario/datos', methods=['GET'])
def obtener_usuario_actual():
    if 'user_id' not in session:
        return jsonify({"status": "error", "message": "No hay sesión activa"}), 401
        
    try:
        connection = db_manager.get_connection()
        cursor = connection.cursor()
        query = "SELECT nombres, apellidos, correo, celular FROM usuarios WHERE id = ?"
        cursor.execute(query, (session['user_id'],))
        usuario = cursor.fetchone()
        cursor.close()
        connection.close()

        if usuario:
            return jsonify({
                "status": "success",
                "data": {
                    "nombres": usuario['nombres'],
                    "apellidos": usuario['apellidos'],
                    "email": usuario['correo'],
                    "celular": usuario['celular']
                }
            })
        else:
            return jsonify({"status": "error", "message": "Usuario no encontrado"}), 404

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/usuario/<int:user_id>', methods=['GET'])
def obtener_usuario(user_id):
    try:
        connection = db_manager.get_connection()
        cursor = connection.cursor()
        query = "SELECT nombres, apellidos, correo, celular FROM usuarios WHERE id = ?"
        cursor.execute(query, (user_id,))
        usuario = cursor.fetchone()
        cursor.close()
        connection.close()

        if usuario:
            return jsonify({
                "status": "success",
                "data": {
                    "nombres": usuario['nombres'],
                    "apellidos": usuario['apellidos'],
                    "email": usuario['correo'],
                    "celular": usuario['celular']
                }
            })
        else:
            return jsonify({"status": "error", "message": "Usuario no encontrado"}), 404

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/usuario/<int:user_id>/detalles', methods=['GET'])
def obtener_detalles_usuario(user_id):
    try:
        connection = db_manager.get_connection()
        cursor = connection.cursor()
        query = """
            SELECT id, nombres, apellidos, tipo_documento, num_documento, 
                   celular, correo, tipo_usuario
            FROM usuarios 
            WHERE id = ?
        """
        cursor.execute(query, (user_id,))
        usuario = cursor.fetchone()
        cursor.close()
        connection.close()

        if usuario:
            return jsonify({
                "status": "success",
                "data": dict(usuario)
            })
        else:
            return jsonify({"status": "error", "message": "Usuario no encontrado"}), 404

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/usuarios/add', methods=['POST'])
def agregar_usuario():
    try:
        data = request.json
        connection = db_manager.get_connection()
        cursor = connection.cursor()
        
        # Verificar si el correo ya existe
        cursor.execute("SELECT id FROM usuarios WHERE correo = ?", (data['email'],))
        if cursor.fetchone():
            cursor.close()
            connection.close()
            return jsonify({
                "status": "error",
                "message": "El correo electrónico ya está registrado"
            }), 400
            
        # Verificar si el número de documento ya existe
        cursor.execute("SELECT id FROM usuarios WHERE num_documento = ?", (data['num_documento'],))
        if cursor.fetchone():
            cursor.close()
            connection.close()
            return jsonify({
                "status": "error",
                "message": "El número de documento ya está registrado"
            }), 400
        
        # Insertar el nuevo usuario
        cursor.execute("""
            INSERT INTO usuarios (
                nombres, apellidos, tipo_documento, num_documento,
                celular, correo, contrasena, tipo_usuario,
                estado, intentos_fallidos
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'activa', 0)
        """, (
            data['nombres'], data['apellidos'], data['tipo_documento'],
            data['num_documento'], data['celular'], data['email'],
            data['password'], data['tipo_usuario']
        ))
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return jsonify({
            "status": "success",
            "message": "Usuario creado exitosamente"
        })
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/usuarios/update/<int:user_id>', methods=['PUT'])
def actualizar_usuario(user_id):
    try:
        data = request.json
        connection = db_manager.get_connection()
        cursor = connection.cursor()
        
        # Verificar si el correo ya existe para otro usuario
        cursor.execute("SELECT id FROM usuarios WHERE correo = ? AND id != ?", 
                    (data['email'], user_id))
        if cursor.fetchone():
            cursor.close()
            connection.close()
            return jsonify({
                "status": "error",
                "message": "El correo electrónico ya está registrado por otro usuario"
            }), 400
            
        # Verificar si el número de documento ya existe para otro usuario
        cursor.execute("SELECT id FROM usuarios WHERE num_documento = ? AND id != ?", 
                    (data['num_documento'], user_id))
        if cursor.fetchone():
            cursor.close()
            connection.close()
            return jsonify({
                "status": "error",
                "message": "El número de documento ya está registrado por otro usuario"
            }), 400
        
        # Actualizar el usuario
        cursor.execute("""
            UPDATE usuarios 
            SET nombres = ?, 
                apellidos = ?,
                tipo_documento = ?,
                num_documento = ?,
                celular = ?,
                correo = ?,
                tipo_usuario = ?
            WHERE id = ?
        """, (
            data['nombres'], data['apellidos'], data['tipo_documento'],
            data['num_documento'], data['celular'], data['email'],
            data['tipo_usuario'], user_id
        ))
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return jsonify({
            "status": "success",
            "message": "Usuario actualizado exitosamente"
        })
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/usuario/actualizar', methods=['POST'])
def actualizar_perfil_usuario():
    if 'user_id' not in session:
        return jsonify({"status": "error", "message": "No hay sesión activa"}), 401
    
    try:
        data = request.json
        connection = db_manager.get_connection()
        cursor = connection.cursor()

        # Verificar si el correo ya existe para otro usuario
        if 'email' in data:
            cursor.execute("SELECT id FROM usuarios WHERE correo = ? AND id != ?", 
                        (data['email'], session['user_id']))
            if cursor.fetchone():
                cursor.close()
                connection.close()
                return jsonify({
                    "status": "error", 
                    "message": "El correo ya está registrado por otro usuario"
                }), 400

        # Actualizar los datos del usuario
        update_query = """
            UPDATE usuarios 
            SET nombres = ?,
                apellidos = ?,
                correo = ?,
                celular = ?
            WHERE id = ?
        """
        cursor.execute(update_query, (
            data['nombres'],
            data['apellidos'],
            data['email'],
            data['celular'],
            session['user_id']
        ))
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return jsonify({
            "status": "success",
            "message": "Perfil actualizado correctamente"
        })

    except Exception as e:
        print(f"Error actualizando perfil: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Error al actualizar el perfil: {str(e)}"
        }), 500

@app.route('/api/actualizar-password', methods=['POST'])
def actualizar_password():
    data = request.json
    email = data.get('email')
    current_password = data.get('current_password')
    new_password = data.get('new_password')

    connection = db_manager.get_connection()
    cursor = connection.cursor()
    
    # Verificar que el token coincida
    query = "SELECT * FROM usuarios WHERE correo = ? AND token_recuperacion = ?"
    cursor.execute(query, (email, current_password))
    usuario = cursor.fetchone()

    if not usuario:
        cursor.close()
        connection.close()
        return jsonify({
            "status": "error",
            "message": "El token temporal no es válido"
        })

    # Actualizar la contraseña, eliminar el token y restaurar el estado
    update_query = """UPDATE usuarios 
                     SET contrasena = ?, 
                         token_recuperacion = NULL, 
                         estado = 'activa',
                         intentos_fallidos = 0 
                     WHERE correo = ?"""
    cursor.execute(update_query, (new_password, email))
    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({
        "status": "success",
        "message": "Contraseña actualizada exitosamente"
    })

@app.route('/api/usuarios/<int:user_id>/toggle-status', methods=['POST'])
def toggle_user_status(user_id):
    try:
        connection = db_manager.get_connection()
        cursor = connection.cursor()
        
        # Obtener estado actual del usuario
        cursor.execute("SELECT estado FROM usuarios WHERE id = ?", (user_id,))
        result = cursor.fetchone()
        
        if not result:
            cursor.close()
            connection.close()
            return jsonify({"status": "error", "message": "Usuario no encontrado"}), 404
        
        # Cambiar el estado
        nuevo_estado = 'bloqueado' if result['estado'] == 'activa' else 'activa'
        cursor.execute("UPDATE usuarios SET estado = ? WHERE id = ?", (nuevo_estado, user_id))
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return jsonify({
            "status": "success",
            "message": f"Usuario {nuevo_estado}",
            "nuevo_estado": nuevo_estado
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/reservas/<int:reserva_id>/update-status', methods=['POST'])
def update_reservation_status(reserva_id):
    try:
        nuevo_estado = request.json.get('estado')
        if nuevo_estado not in ['activa', 'completada', 'cancelada']:
            return jsonify({"status": "error", "message": "Estado inválido"}), 400
            
        connection = db_manager.get_connection()
        cursor = connection.cursor()
        
        # Obtener el ID de la mesa antes de actualizar la reserva
        cursor.execute("SELECT mesa_id FROM reservas WHERE id = ?", (reserva_id,))
        resultado = cursor.fetchone()
        if not resultado:
            cursor.close()
            connection.close()
            return jsonify({"status": "error", "message": "Reserva no encontrada"}), 404
            
        mesa_id = resultado['mesa_id']
        
        # Actualizar el estado de la reserva
        cursor.execute("UPDATE reservas SET estado = ? WHERE id = ?", (nuevo_estado, reserva_id))
        
        # Actualizar el estado de la mesa según el nuevo estado de la reserva
        if nuevo_estado in ['completada', 'cancelada']:
            # Verificar si hay otras reservas activas para esta mesa
            cursor.execute("""
                SELECT COUNT(*) as reservas_activas 
                FROM reservas 
                WHERE mesa_id = ? AND estado = 'activa' AND id != ?
            """, (mesa_id, reserva_id))
            
            otras_reservas = cursor.fetchone()['reservas_activas']
            
            if otras_reservas == 0:
                # Si no hay otras reservas activas, marcar la mesa como disponible
                cursor.execute("UPDATE mesas SET estado = 'disponible' WHERE id = ?", (mesa_id,))
        
        connection.commit()
        
        # Si la reserva se marca como completada, crear el comprobante
        if nuevo_estado == 'completada':
            success, message = db_manager.crear_comprobante(reserva_id)
            if not success:
                cursor.close()
                connection.close()
                return jsonify({
                    "status": "warning",
                    "message": f"Reserva completada pero hubo un error al crear el comprobante: {message}"
                })
        
        cursor.close()
        connection.close()
        
        return jsonify({
            "status": "success",
            "message": f"Reserva actualizada a {nuevo_estado}",
            "nuevo_estado": nuevo_estado
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/menu/add', methods=['POST'])
def add_menu_item():
    try:
        data = request.json
        connection = db_manager.get_connection()
        cursor = connection.cursor()
        
        cursor.execute("""
            INSERT INTO alimentos (nombre, descripcion, tipo_alimento, gramaje, precio, estado, url_imagen)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (data['nombre'], data['descripcion'], data['tipo_alimento'], data['gramaje'], data['precio'], data['estado'], data.get('url_imagen')))
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return jsonify({
            "status": "success",
            "message": "Plato agregado correctamente"
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/mesas/add', methods=['POST'])
def add_mesa():
    try:
        data = request.json
        connection = db_manager.get_connection()
        cursor = connection.cursor()
        
        print("Estado recibido:", repr(data.get("estado")))
        cursor.execute("""
            INSERT INTO mesas (capacidad, ubicacion, estado)
            VALUES (?, ?, ?)
        """, (
            data['capacidad'], 
            data['ubicacion'], 
            data['estado'] 
        ))
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return jsonify({
            "status": "success",
            "message": "Mesa agregada correctamente"
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# TODO: implementar logica de editar mesas para usar este metodo
@app.route('/api/mesas/<int:id>', methods=['GET'])
def get_mesa(id):
    try:
        connection = db_manager.get_connection()
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        
        cursor.execute("SELECT * FROM mesas WHERE id = ?", (id,))
        mesa = cursor.fetchone()
        
        if mesa:
            mesa_dict = dict(mesa)
            cursor.close()
            connection.close()
            return jsonify({
                "status": "success",
                "mesa": mesa_dict
            })
        else:
            cursor.close()
            connection.close()
            return jsonify({
                "status": "error",
                "message": "Mesa no encontrada"
            }), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/mesas/update/<int:id>', methods=['PUT'])
def update_mesa(id):
    try:
        data = request.json  # Datos enviados desde JS
        connection = db_manager.get_connection()
        cursor = connection.cursor()

        # Ejecutar la actualización
        cursor.execute("""
            UPDATE mesas
            SET capacidad = ?, ubicacion = ?, estado = ?
            WHERE id = ?
        """, (data['capacidad'], data['ubicacion'], data['estado'], id))

        connection.commit()

        # Verificar si realmente se modificó algo
        if cursor.rowcount == 0:
            return jsonify({"status": "error", "message": "Mesa no encontrada"}), 404

        cursor.close()
        connection.close()

        return jsonify({"status": "success", "message": "Mesa actualizada correctamente ✅"})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    
@app.route('/api/menu/<int:id>', methods=['GET'])
def get_menu_item(id):
    try:
        connection = db_manager.get_connection()
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        
        cursor.execute("SELECT * FROM alimentos WHERE id = ?", (id,))
        plato = cursor.fetchone()
        
        if plato:
            plato_dict = dict(plato)
            cursor.close()
            connection.close()
            return jsonify({
                "status": "success",
                "plato": plato_dict
            })
        else:
            cursor.close()
            connection.close()
            return jsonify({
                "status": "error",
                "message": "Plato no encontrado"
            }), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    
@app.route('/api/menu/update', methods=['POST'])
def update_menu_item():
    try:
        data = request.json
        connection = db_manager.get_connection()
        cursor = connection.cursor()
        
        cursor.execute("""
            UPDATE alimentos 
            SET nombre = ?, descripcion = ?, tipo_alimento = ?, gramaje = ?, precio = ?, estado = ?, url_imagen = ?
            WHERE id = ?
        """, (data['nombre'], data['descripcion'], data['tipo_alimento'], data['gramaje'], 
              data['precio'], data['estado'], data.get('url_imagen'), data['id']))
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return jsonify({
            "status": "success",
            "message": "Plato actualizado correctamente"
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/reservas/<int:reserva_id>/update', methods=['PUT'])
def update_reservation(reserva_id):
    try:
        data = request.json
        connection = db_manager.get_connection()
        cursor = connection.cursor()
        
        cursor.execute("""
            UPDATE reservas 
            SET mesa_id = ?, fecha = ?, hora = ?, num_personas = ?, estado = ?
            WHERE id = ?
        """, (data['mesa_id'], data['fecha'], data['hora'], data['num_personas'], data['estado'], reserva_id))
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return jsonify({
            "status": "success",
            "message": "Reserva actualizada correctamente"
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/menu/<int:plato_id>', methods=['PUT', 'DELETE'])
def manage_menu_item(plato_id):
    try:
        connection = db_manager.get_connection()
        cursor = connection.cursor()
        
        if request.method == 'DELETE':
            cursor.execute("DELETE FROM alimentos WHERE id = ?", (plato_id,))
            mensaje = "Plato eliminado correctamente"
        else:  # PUT
            data = request.json
            cursor.execute("""
                UPDATE alimentos 
                SET nombre = ?, descripcion = ?, tipo_alimento = ?, gramaje = ?, precio = ?, estado = ?, url_imagen = ?
                WHERE id = ?
            """, (data['nombre'], data['descripcion'], data['tipo_alimento'], data['gramaje'], 
                  data['precio'], data['estado'], data.get('url_imagen'), plato_id))
            mensaje = "Plato actualizado correctamente"
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return jsonify({
            "status": "success",
            "message": mensaje
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/reservas/<int:reserva_id>/comprobante', methods=['GET'])
def get_comprobante(reserva_id):
    try:
        comprobante = db_manager.get_comprobante(reserva_id)
        if comprobante:
            return jsonify({
                "status": "success",
                "data": comprobante
            })
        else:
            return jsonify({
                "status": "error",
                "message": "Comprobante no encontrado"
            }), 404
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()  # Elimina todos los datos de la sesión
    return jsonify({"status": "success", "message": "Sesión cerrada correctamente"})

if __name__ == '__main__':
    app.run(debug=True)