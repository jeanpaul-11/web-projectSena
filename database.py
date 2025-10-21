import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class DatabaseManager:
    def __init__(self):
        self.db_config = {
            'dbname': os.getenv('DB_NAME', 'restaurant_jp_db'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', ''),
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432')
        }

    def get_connection(self):
        connection = psycopg2.connect(**self.db_config, cursor_factory=RealDictCursor)
        return connection

    def get_user_stats(self):
        """Obtener estadísticas de usuarios"""
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            
            # Total de usuarios
            cursor.execute("SELECT COUNT(*) as total FROM usuarios")
            total = cursor.fetchone()['total']
            
            # Usuarios activos
            cursor.execute("SELECT COUNT(*) as activos FROM usuarios WHERE estado = 'activa'")
            activos = cursor.fetchone()['activos']
            
            # Usuarios bloqueados
            cursor.execute("SELECT COUNT(*) as bloqueados FROM usuarios WHERE estado = 'bloqueado'")
            bloqueados = cursor.fetchone()['bloqueados']
            
            # Lista de usuarios
            cursor.execute("""
                SELECT id, nombres || ' ' || apellidos as nombre, correo, estado, tipo_usuario 
                FROM usuarios
                ORDER BY id DESC
            """)
            usuarios = cursor.fetchall()
            
            cursor.close()
            connection.close()
            
            return {
                "total": total,
                "activos": activos,
                "bloqueados": bloqueados,
                "lista": usuarios
            }
        except psycopg2.Error as e:
            print(f"Error obteniendo estadísticas de usuarios: {e}")
            return None

    def get_reservation_stats(self):
        """Obtener estadísticas de reservas"""
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            
            # Total de reservas activas
            cursor.execute("SELECT COUNT(*) as activas FROM reservas WHERE estado = 'activa'")
            activas = cursor.fetchone()['activas']
            
            # Reservas completadas
            cursor.execute("SELECT COUNT(*) as completadas FROM reservas WHERE estado = 'completada'")
            completadas = cursor.fetchone()['completadas']
            
            # Reservas canceladas
            cursor.execute("SELECT COUNT(*) as canceladas FROM reservas WHERE estado = 'cancelada'")
            canceladas = cursor.fetchone()['canceladas']
            
            # Lista de reservas con información del cliente
            cursor.execute("""
                SELECT r.id, u.nombres || ' ' || u.apellidos as cliente, r.mesa_id,
                       r.fecha, r.hora, r.num_personas, r.estado
                FROM reservas r
                JOIN usuarios u ON r.cliente_id = u.id
                ORDER BY r.fecha DESC, r.hora DESC
            """)
            reservas = cursor.fetchall()
            
            cursor.close()
            connection.close()
            
            return {
                "activas": activas,
                "completadas": completadas,
                "canceladas": canceladas,
                "lista": reservas
            }
        except psycopg2.Error as e:
            print(f"Error obteniendo estadísticas de reservas: {e}")
            return None

    def get_comprobante(self, reserva_id):
        """Obtener el comprobante de una reserva"""
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            
            # Obtener todos los detalles de la reserva, cliente y pedidos
            cursor.execute("""
                SELECT 
                    r.id as reserva_id, 
                    r.fecha,
                    r.hora,
                    m.ubicacion as mesa_ubicacion,
                    u.nombres, 
                    u.apellidos, 
                    u.num_documento, 
                    u.celular, 
                    u.correo,
                    c.subtotal,
                    c.total,
                    c.fecha_emision,
                    string_agg(a.nombre || ' (x' || p.cantidad || ' = $' || (a.precio * p.cantidad) || ')', ', ') as productos,
                    string_agg(a.nombre || ' x' || p.cantidad, ', ') as nombre_producto
                FROM reservas r
                JOIN usuarios u ON r.cliente_id = u.id
                JOIN mesas m ON r.mesa_id = m.id
                JOIN comprobantes c ON r.id = c.reserva_id
                LEFT JOIN pedidos p ON r.id = p.reserva_id
                LEFT JOIN alimentos a ON p.alimento_id = a.id
                WHERE r.id = %s
                GROUP BY r.id
            """, (reserva_id,))
            
            result = cursor.fetchone()
            
            if not result:
                cursor.close()
                connection.close()
                return None
                
            # Formatear los datos
            comprobante = dict(result)
            
            cursor.close()
            connection.close()
            return comprobante
            
        except psycopg2.Error as e:
            print(f"Error obteniendo comprobante: {e}")
            return None

    def crear_comprobante(self, reserva_id):
        """Crear un comprobante para una reserva completada"""
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            
            # Verificar si ya existe un comprobante para esta reserva
            cursor.execute("SELECT id FROM comprobantes WHERE reserva_id = %s", (reserva_id,))
            if cursor.fetchone():
                cursor.close()
                connection.close()
                return False, "Ya existe un comprobante para esta reserva"
            
            # Obtener información de los pedidos y calcular el total
            cursor.execute("""
                SELECT SUM(a.precio * p.cantidad) as subtotal, 
                       string_agg(a.nombre || ' x' || p.cantidad, ', ') as nombre_producto
                FROM pedidos p
                JOIN alimentos a ON p.alimento_id = a.id
                WHERE p.reserva_id = %s
                GROUP BY p.reserva_id
            """, (reserva_id,))
            
            result = cursor.fetchone()
            
            if not result:
                subtotal = 0
                nombre_producto = "Sin productos"
            else:
                subtotal = result['subtotal']
                nombre_producto = result['nombre_producto']
            
            total = subtotal * 1.19  # Incluyendo IVA del 19%
            
            # Insertar el comprobante
            cursor.execute("""
                INSERT INTO comprobantes (
                    reserva_id, subtotal, total
                ) VALUES (%s, %s, %s)
            """, (reserva_id, subtotal, total))
            
            connection.commit()
            cursor.close()
            connection.close()
            return True, "Comprobante creado exitosamente"
            
        except psycopg2.Error as e:
            print(f"Error creando comprobante: {e}")
            return False, f"Error al crear el comprobante: {str(e)}"

    def get_menu_stats(self):
        """Obtener estadísticas del menú"""
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            
            # Total de platos
            cursor.execute("SELECT COUNT(*) as total FROM alimentos")
            total = cursor.fetchone()['total']
            
            # Lista de platos
            cursor.execute("""
                SELECT id, nombre, tipo_alimento, gramaje, precio
                FROM alimentos
                ORDER BY tipo_alimento, nombre
            """)
            platos = [dict(row) for row in cursor.fetchall()]
            
            # Agrupar platos por tipo
            cursor.execute("""
                SELECT tipo_alimento, COUNT(*) as cantidad
                FROM alimentos
                GROUP BY tipo_alimento
            """)
            tipos = [dict(row) for row in cursor.fetchall()]
            
            cursor.close()
            connection.close()
            
            return {
                "total": total,
                "tipos": tipos,
                "lista": platos
            }
        except psycopg2.Error as e:
            print(f"Error obteniendo estadísticas del menú: {e}")
            return None
        
    def get_mesa_stats(self):
        """Obtener estadísticas de las mesas"""
        try:
            connection = self.get_connection()
            # PostgreSQL with RealDictCursor already handles row as dict
            cursor = connection.cursor()
        
            # Total de mesas
            cursor.execute("SELECT COUNT(*) as total FROM mesas")
            total = cursor.fetchone()["total"]

            # Lista de mesas
            cursor.execute("""
                SELECT id, capacidad, ubicacion, estado
                FROM mesas
                ORDER BY id
            """)
            mesas = [dict(row) for row in cursor.fetchall()]

            cursor.close()
            connection.close()

            return {
                "total": total,
                "lista": mesas
            }
        except psycopg2.Error as e:
            print(f"Error obteniendo estadísticas de las mesas: {e}")
            return None
    
    def validar_usuario(self, correo, contrasena):
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            
            # Primero verificar si el usuario existe y su estado
            check_query = "SELECT * FROM usuarios WHERE correo = %s"
            cursor.execute(check_query, (correo,))
            usuario = cursor.fetchone()
            
            if not usuario:
                cursor.close()
                connection.close()
                return {"status": "error", "message": "Usuario no encontrado"}
            
            # Verificar si la cuenta está bloqueada
            if usuario['estado'] == 'bloqueado':
                cursor.close()
                connection.close()
                return {"status": "error", "message": "Cuenta bloqueada. Contacte al administrador"}
            
            # Si tiene token de recuperación, solo puede iniciar sesión con el token
            if usuario['token_recuperacion']:
                if contrasena != usuario['token_recuperacion']:
                    cursor.close()
                    connection.close()
                    return {"status": "error", "message": "Debe usar el token enviado a su correo"}
                    
            # Verificar la contraseña
            if contrasena == usuario['contrasena'] or (usuario['token_recuperacion'] and contrasena == usuario['token_recuperacion']):
                # Actualizar último login y reiniciar intentos fallidos
                cursor.execute("""
                    UPDATE usuarios 
                    SET intentos_fallidos = 0,
                        ultimo_login = CURRENT_TIMESTAMP 
                    WHERE correo = %s
                """, (correo,))
                connection.commit()
                
                cursor.close()
                connection.close()
                return {
                    "status": "success", 
                    "message": "Usuario validado correctamente",
                    "data": {
                        "tipo_usuario": usuario['tipo_usuario'],
                        "id": usuario['id'],
                        "nombres": usuario['nombres'],
                        "token_recuperacion": usuario['token_recuperacion']
                    }
                }
            else:
                # Incrementar intentos fallidos
                intentos = usuario['intentos_fallidos'] + 1 if usuario['intentos_fallidos'] else 1
                nuevo_estado = 'bloqueado' if intentos >= 3 else usuario['estado']
                
                cursor.execute("""
                    UPDATE usuarios 
                    SET intentos_fallidos = ?, 
                        estado = ? 
                    WHERE correo = %s
                """, (intentos, nuevo_estado, correo))
                connection.commit()
                
                mensaje = "Cuenta bloqueada por múltiples intentos fallidos" if intentos >= 3 else f"Contraseña incorrecta. Intentos restantes: {3 - intentos}"
                
                cursor.close()
                connection.close()
                return {"status": "error", "message": mensaje}
        except psycopg2.Error as e:
            return {"status": "error", "message": f"Error validando usuario: {e}"}
        
    def insertar_usuario(self, nombres, apellidos, tipo_documento, num_documento, celular, email, password):
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            
            # Verificar si el correo ya está registrado
            cursor.execute("SELECT id FROM usuarios WHERE correo = %s", (email,))
            if cursor.fetchone():
                cursor.close()
                connection.close()
                return {"status": "error", "message": "El correo ya está registrado"}
            
            # Verificar si el número de documento ya está registrado
            cursor.execute("SELECT id FROM usuarios WHERE num_documento = %s", (num_documento,))
            if cursor.fetchone():
                cursor.close()
                connection.close()
                return {"status": "error", "message": "El número de documento ya está registrado"}
            
            insert_query = """
                INSERT INTO usuarios (
                    tipo_usuario, nombres, apellidos, tipo_documento, 
                    num_documento, celular, correo, contrasena, 
                    intentos_fallidos, estado
                ) VALUES (
                    '0', %s, %s, %s, %s, %s, %s, %s, 0, 'activa'
                )
            """
            values = (nombres, apellidos, tipo_documento, num_documento, celular, email, password)
            cursor.execute(insert_query, values)
            connection.commit()
            cursor.close()
            connection.close()
            return {"status": "success", "message": "Usuario registrado correctamente"}
        except psycopg2.Error as e:
            return {"status": "error", "message": f"Error insertando usuario: {e}"}


    def insertar_mesa(self, capacidad, ubicacion, estado):
        try:
            cursor = self.connection.cursor()
            insert_query = "INSERT INTO mesas (capacidad, ubicacion, estado) VALUES (%s, %s, %s)"
            values = (capacidad, ubicacion, estado)
            cursor.execute(insert_query, values)
            self.connection.commit() 
            print("mesa insertada correctamente")
        except psycopg2.Error as e:
            print(f"Error insertando mesa: {e}")
            
    def insertar_pedidos(self, plato_id, cantidad, precio_unitario):
        try:
            cursor = self.connection.cursor()
            insert_query = "INSERT INTO pedidos (reserva_id, plato_id, cantidad, precio_unitario) VALUES (%s, %s, %s, %s)"
            values = (plato_id, cantidad, precio_unitario)
            cursor.execute(insert_query, values)
            self.connection.commit()
            print("pedido insertado correctamente")
        except psycopg2.Error as e:
            print(f"Error insertando pedido: {e}")

    def insertar_reserva(self, fecha, hora, num_personas):
        try:
            cursor = self.connection.cursor()
            insert_query = "INSERT INTO reservas (fecha, hora, num_personas) VALUES (%s, %s, %s)"
            values = (fecha, hora, num_personas)
            cursor.execute(insert_query, values)
            self.connection.commit()
            print("reserva insertado correctamente")
        except psycopg2.Error as e:
            print(f"Error insertando reserva: {e}")

    def crear_reserva(self, cliente_id, fecha, hora, num_personas, alimentos=None):
        from email_service import EmailService
        email_service = EmailService()
        
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            
            # Buscar una mesa adecuada que no esté reservada para esa fecha y hora
            cursor.execute("""
                SELECT m.id FROM mesas m 
                WHERE m.capacidad >= %s AND m.id NOT IN (
                    SELECT mesa_id FROM reservas 
                    WHERE fecha = %s AND hora = %s AND estado = 'activa'
                )
                LIMIT 1
            """, (num_personas, fecha, hora))
            
            mesa = cursor.fetchone()
            if not mesa:
                cursor.close()
                connection.close()
                return False, "No hay mesas disponibles para esa fecha y hora"
            
            mesa_id = mesa['id']
            
            # Obtener información del cliente
            cursor.execute("SELECT nombres, apellidos, correo FROM usuarios WHERE id = %s", (cliente_id,))
            cliente = cursor.fetchone()
            if not cliente:
                cursor.close()
                connection.close()
                return False, "Cliente no encontrado"
            
            # Crear la reserva
            cursor.execute("""
                INSERT INTO reservas (cliente_id, mesa_id, fecha, hora, num_personas, estado)
                VALUES (%s, %s, %s, %s, %s, 'activa')
            """, (cliente_id, mesa_id, fecha, hora, num_personas))
            
            # Get the id of the inserted reservation
            cursor.execute("SELECT LASTVAL()")
            reserva_id = cursor.fetchone()['lastval']
            
            # Lista para almacenar detalles de platos para el correo
            platos_email = []
            
            # Si hay alimentos seleccionados, registrarlos
            if alimentos:
                for alimento in alimentos:
                    cursor.execute("""
                        INSERT INTO pedidos (reserva_id, alimento_id, cantidad)
                        VALUES (%s, %s, %s)
                    """, (reserva_id, alimento['id'], alimento['cantidad']))
                    
                    # Obtener información del plato para el correo
                    cursor.execute("SELECT nombre, precio FROM alimentos WHERE id = %s", (alimento['id'],))
                    plato_info = cursor.fetchone()
                    if plato_info:
                        platos_email.append({
                            'nombre': plato_info['nombre'],
                            'cantidad': alimento['cantidad'],
                            'precio': plato_info['precio']
                        })
            
            # Actualizar estado de la mesa
            cursor.execute("""
                UPDATE mesas SET estado = 'reservada' WHERE id = %s
            """, (mesa_id,))
            
            connection.commit()
            
            # Enviar correo de confirmación
            nombre_completo = f"{cliente['nombres']} {cliente['apellidos']}"
            email_service.enviar_correo_reserva(
                destinatario=cliente['correo'],
                nombre=nombre_completo,
                fecha=fecha,
                hora=hora,
                num_personas=num_personas,
                platos=platos_email
            )
            
            cursor.close()
            connection.close()
            return True, "Reserva creada exitosamente"
            
        except psycopg2.Error as e:
            print(f"Error al crear reserva: {str(e)}")
            return False, "Error al procesar la reserva"