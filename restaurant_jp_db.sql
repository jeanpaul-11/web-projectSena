CREATE DATABASE restaurant_jp_db;

use restaurant_jp_db;

CREATE TABLE mesas(
    id INT AUTO_INCREMENT PRIMARY KEY,
    capacidad INT,
    ubicacion VARCHAR(50),
    estado ENUM('disponible', 'opcupada', 'reservada')
);
CREATE TABLE clientes(
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    celular VARCHAR(13) NOT NULL,
    correo VARCHAR(20),
    tipo_documento VARCHAR(2) NOT NULL,
    num_documento VARCHAR(10) NOT NULL
);
CREATE TABLE reservas(
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT NOT NULL,
    mesa_id INT NOT NULL,
    fecha DATE NOT NULL,
    hora TIME NOT NULL,
    num_personas INT,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id),
    FOREIGN KEY (mesa_id) REFERENCES mesas(id)
);
CREATE TABLE pedidos(
    id INT AUTO_INCREMENT PRIMARY KEY,
    reserva_id INT,
    plato_id INT,
    cantidad INT,
    precio_unitario DECIMAL(10, 3),
    FOREIGN KEY (reserva_id) REFERENCES reservas(id)
)