import sqlite3

class DatabaseManager:
    def __init__(self):
        self.db_path = 'restaurant_jp_db.sqlite'

    def get_connection(self):
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def validar_usuario(self, correo, contrasena):
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            query = "SELECT * FROM usuarios WHERE correo = ? AND contrasena = ?"
            values = (correo, contrasena)
            cursor.execute(query, values)
            resultado = cursor.fetchone()
            cursor.close()
            connection.close()
            if resultado:
                return {
                    "status": "success", 
                    "message": "Usuario validado correctamente",
                    "data": {
                        "tipo_usuario": resultado['tipo_usuario'],
                        "id": resultado['id'],
                        "nombres": resultado['nombres']
                    }
                }
            else:
                return {"status": "error", "message": "Correo o contraseña incorrectos"}
        except sqlite3.Error as e:
            return {"status": "error", "message": f"Error validando usuario: {e}"}
        
    def insertar_usuario(self, nombres, apellidos, tipo_documento, num_documento, celular, email, password):
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            insert_query = """
                INSERT INTO usuarios (nombres, apellidos, tipo_documento, num_documento, celular, correo, contrasena) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            values = (nombres, apellidos, tipo_documento, num_documento, celular, email, password)
            cursor.execute(insert_query, values)
            connection.commit()
            cursor.close()
            connection.close()
            return {"status": "success", "message": "Usuario registrado correctamente"}
        except sqlite3.Error as e:
            return {"status": "error", "message": f"Error insertando usuario: {e}"}


    def insertar_mesa(self, capacidad, ubicacion, estado):
        try:
            cursor = self.connection.cursor()
            insert_query = "INSERT INTO mesas (capacidad, ubicacion, estado) VALUES (%s, %s, %s)"
            values = (capacidad, ubicacion, estado)
            cursor.execute(insert_query, values)
            self.connection.commit() 
            print("mesa insertada correctamente")
        except sqlite3.Error as e:
            print(f"Error insertando mesa: {e}")
            
    def insertar_pedidos(self, plato_id, cantidad, precio_unitario):
        try:
            cursor = self.connection.cursor()
            insert_query = "INSERT INTO pedidos (reserva_id, plato_id, cantidad, precio_unitario) VALUES (%s, %s, %s, %s)"
            values = (plato_id, cantidad, precio_unitario)
            cursor.execute(insert_query, values)
            self.connection.commit()
            print("pedido insertado correctamente")
        except sqlite3.Error as e:
            print(f"Error insertando pedido: {e}")

    def insertar_reserva(self, fecha, hora, num_personas):
        try:
            cursor = self.connection.cursor()
            insert_query = "INSERT INTO reservas (fecha, hora, num_personas) VALUES (%s, %s, %s)"
            values = (fecha, hora, num_personas)
            cursor.execute(insert_query, values)
            self.connection.commit()
            print("reserva insertado correctamente")
        except sqlite3.Error as e:
            print(f"Error insertando reserva: {e}")

    def crear_reserva(self, cliente_id, fecha, hora, num_personas, platos=None):
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            
            # Buscar una mesa adecuada que no esté reservada para esa fecha y hora
            cursor.execute("""
                SELECT m.id FROM mesas m 
                WHERE m.capacidad >= ? AND m.id NOT IN (
                    SELECT mesa_id FROM reservas 
                    WHERE fecha = ? AND hora = ? AND estado = 'disponible'
                )
                LIMIT 1
            """, (num_personas, fecha, hora))
            
            mesa = cursor.fetchone()
            if not mesa:
                return False, "No hay mesas disponibles para esa fecha y hora"
            
            mesa_id = mesa['id']
            
            print("va a a crear la reserva....")
            
            # Crear la reserva
            cursor.execute("""
                INSERT INTO reservas (cliente_id, mesa_id, fecha, hora, num_personas, estado)
                VALUES (?, ?, ?, ?, ?, 'activa')
            """, (cliente_id, mesa_id, fecha, hora, num_personas))
            
            reserva_id = cursor.lastrowid
            
            print("va a validar si hay platos....")
             
            # Si hay platos seleccionados, registrarlos
            if platos:
                for plato in platos:
                    cursor.execute("""
                        INSERT INTO pedidos (reserva_id, plato_id, cantidad, precio_unitario)
                        VALUES (?, ?, ?, ?)
                    """, (reserva_id, plato['id'], plato['cantidad'], plato['precio']))
            
            print("termino validar y inserto platos....")
            
            connection.commit()
            cursor.close()
            connection.close()
            return True, "Reserva creada exitosamente"
            
        except sqlite3.Error as e:
            print(f"Error al crear reserva: {str(e)}")
            return False, "Error al procesar la reserva"