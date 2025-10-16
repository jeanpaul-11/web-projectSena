-- Activar las claves foráneas
PRAGMA foreign_keys = ON;

CREATE TABLE usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo_usuario TEXT CHECK (tipo_usuario IN ('admin', 'empleado', 'cliente')),
    nombres TEXT NOT NULL,
    apellidos TEXT NOT NULL,
    tipo_documento TEXT NOT NULL,
    num_documento TEXT NOT NULL UNIQUE,
    celular TEXT,
    correo TEXT NOT NULL UNIQUE,
    contrasena TEXT NOT NULL,
    token_recuperacion TEXT,
    intentos_fallidos INTEGER DEFAULT 0,
    estado TEXT CHECK (estado IN ('activa', 'bloqueado', 'inactiva')),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ultimo_login TIMESTAMP
);

CREATE TABLE mesas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    capacidad INTEGER NOT NULL,
    ubicacion TEXT NOT NULL,
    estado TEXT CHECK (estado IN ('disponible', 'ocupada', 'reservada', 'mantenimiento')) DEFAULT 'disponible'
);

CREATE TABLE alimentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    descripcion TEXT,
    tipo_alimento TEXT CHECK (tipo_alimento IN ('entrada', 'plato_fuerte', 'postre', 'bebida')) NOT NULL,
    gramaje INTEGER,
    precio DECIMAL(10,2) NOT NULL,
    estado TEXT CHECK (estado IN ('disponible', 'agotado', 'descontinuado')) DEFAULT 'disponible'
    url_imagen TEXT
);

CREATE TABLE reservas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER NOT NULL,
    mesa_id INTEGER NOT NULL,
    fecha DATE NOT NULL,
    hora TIME NOT NULL,
    num_personas INTEGER NOT NULL,
    estado TEXT CHECK (estado IN ('pendiente', 'activa', 'cancelada', 'completada')) DEFAULT 'pendiente',
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cliente_id) REFERENCES usuarios(id),
    FOREIGN KEY (mesa_id) REFERENCES mesas(id)
);

CREATE TABLE pedidos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reserva_id INTEGER NOT NULL,
    alimento_id INTEGER NOT NULL,
    cantidad INTEGER NOT NULL CHECK (cantidad > 0),
    estado TEXT CHECK (estado IN ('pendiente', 'en_preparacion', 'listo', 'entregado', 'cancelado')) DEFAULT 'pendiente',
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (reserva_id) REFERENCES reservas(id),
    FOREIGN KEY (alimento_id) REFERENCES alimentos(id)
);

CREATE TABLE comprobantes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reserva_id INTEGER NOT NULL UNIQUE,
    subtotal DECIMAL(10,2) NOT NULL,
    total DECIMAL(10,2) NOT NULL,
    fecha_emision TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (reserva_id) REFERENCES reservas(id)
);

-- Crear índices para mejorar el rendimiento
CREATE INDEX idx_reservas_cliente ON reservas(cliente_id);
CREATE INDEX idx_reservas_mesa ON reservas(mesa_id);
CREATE INDEX idx_pedidos_reserva ON pedidos(reserva_id);
CREATE INDEX idx_pedidos_alimento ON pedidos(alimento_id);
CREATE INDEX idx_comprobantes_reserva ON comprobantes(reserva_id);