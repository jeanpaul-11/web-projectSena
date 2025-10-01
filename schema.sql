-- Activar las claves foráneas
PRAGMA foreign_keys = ON;
CREATE TABLE mesas(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    capacidad INTEGER,
    ubicacion TEXT,
    estado TEXT CHECK (estado IN ('disponible', 'ocupada', 'reservada'))
);

CREATE TABLE clientes(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    celular TEXT NOT NULL,
    correo TEXT,
    tipo_documento TEXT NOT NULL,
    num_documento TEXT NOT NULL
);

CREATE TABLE reservas(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER NOT NULL,
    mesa_id INTEGER NOT NULL,
    fecha DATE NOT NULL,
    hora TIME NOT NULL,
    num_personas INTEGER,
    estado TEXT CHECK (estado IN ('activa', 'cancelada', 'completada')),
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id),
    FOREIGN KEY (mesa_id) REFERENCES mesas(id)
);

CREATE TABLE alimentos(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo_alimento TEXT,
    nombre TEXT,
    gramaje INTEGER,
    precio INTEGER
);

CREATE TABLE pedidos(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reserva_id INTEGER,
    plato_id INTEGER,
    cantidad INTEGER,
    precio_unitario REAL,
    precio_total REAL,
    estado TEXT CHECK (estado IN ('sin atender', 'atendido')), 
    FOREIGN KEY (reserva_id) REFERENCES reservas(id),
    FOREIGN KEY (plato_id) REFERENCES alimentos(id)
);

CREATE TABLE usuarios(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo_usuario TEXT,
    nombres TEXT NOT NULL,
    apellidos TEXT,
    tipo_documento TEXT NOT NULL,
    num_documento TEXT NOT NULL,
    celular TEXT,
    correo TEXT NOT NULL,
    contrasena TEXT NOT NULL,
    token_recuperacion TEXT,
    estado TEXT,
    fecha_creacion_perfil TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ultimo_login TIMESTAMP
);

CREATE TABLE comprobantes(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_producto TEXT,
    num_documento TEXT,
    celular TEXT,
    correo TEXT,
    subtotal INTEGER,
    total INTEGER
);