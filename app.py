from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from database import DatabaseManager
from email_service import EmailService
import random
import string
from flask_cors import CORS

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
def clientes():
    return render_template('clientes.html', title='Clientes')

@app.route('/empleado')
def empleado():
    return render_template('empleado.html', title='Panel de Empleado')

@app.route('/admin')
def admin():
    return render_template('admin.html', title='Panel de Administrador')

@app.route('/reservas')
def reservas():
    return render_template('reservas.html', title='Reservas')

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
    return jsonify(resultado)

@app.route('/recuperar-clave', methods=['POST'])
def recuperar_clave():
    data = request.json
    email = data.get('email')

    # Verificar si el email existe en la base de datos
    cursor = db_manager.connection.cursor(dictionary=True)
    query = "SELECT * FROM usuarios WHERE correo = %s"
    cursor.execute(query, (email,))
    usuario = cursor.fetchone()

    if not usuario:
        return jsonify({
            "status": "error",
            "message": "No existe una cuenta con este correo electrónico"
        })

    # Generar token aleatorio
    token = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

    # Guardar el token en la base de datos
    update_query = "UPDATE usuarios SET token_recuperacion = %s WHERE correo = %s"
    cursor.execute(update_query, (token, email))
    db_manager.connection.commit()

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

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()  # Elimina todos los datos de la sesión
    return jsonify({"status": "success", "message": "Sesión cerrada correctamente"})

if __name__ == '__main__':
    app.run(debug=True)