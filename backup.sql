BEGIN;

CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    tipo_usuario TEXT CHECK (tipo_usuario IN ('0', '1', '2')),
    nombres TEXT NOT NULL,
    apellidos TEXT NOT NULL,
    tipo_documento TEXT NOT NULL,
    num_documento TEXT NOT NULL,
    celular TEXT,
    correo TEXT NOT NULL,
    contrasena TEXT NOT NULL,
    token_recuperacion TEXT,
    intentos_fallidos INTEGER DEFAULT 0,
    estado TEXT CHECK (estado IN ('activa', 'bloqueado', 'inactiva')),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ultimo_login TIMESTAMP
);
INSERT INTO usuarios VALUES(1,'0','Juan','Pérez','CC','1234567890','3001234567','cliente@email.com','123456',NULL,0,'activa','2025-09-26 21:54:30',NULL);
INSERT INTO usuarios VALUES(2,'2','Jean Paul','Cañon Cadena','CC','4444','3057709563','admin@gmail.com','222',NULL,0,'activa','2025-09-26 22:15:29','2025-10-02 23:14:10');
INSERT INTO usuarios VALUES(3,'1','Martha','Palacios','CC','1333567765','3145556789','empleado@gmail.com','123',NULL,0,'activa','2025-09-30 00:25:32',NULL);
INSERT INTO usuarios VALUES(4,NULL,'Roberto','Ramirez','CC','1009899099','222222','rob@gmail.com','123',NULL,0,'activa','2025-10-02 01:20:24',NULL);
INSERT INTO usuarios VALUES(5,NULL,'Carlos','Palacios','PAS','222233','222222','car@gmail.com','123',NULL,0,'activa','2025-10-02 01:32:59',NULL);
INSERT INTO usuarios VALUES(6,NULL,'carlos','palacios','CC','15912375','3057709563','jep@gmail.com','123',NULL,0,'bloqueado','2025-10-02 01:33:38','2025-10-02 23:14:10');
INSERT INTO usuarios VALUES(7,'0','Jean Paul','Cadena','CC','777','8888','canon@outlook.com','123',NULL,0,'activa','2025-10-03 19:59:24','2025-10-03 22:00:52');
INSERT INTO usuarios VALUES(8,'0','Santiago','Lopez','CC','1023379717','3224714919','edercadena707@gmail.com','santi10237.',NULL,0,'activa','2025-10-07 15:53:40','2025-10-07 15:54:34');
CREATE TABLE mesas (
    id SERIAL PRIMARY KEY,
    capacidad INTEGER NOT NULL,
    ubicacion TEXT NOT NULL,
    estado TEXT CHECK (estado IN ('disponible', 'ocupada', 'reservada', 'mantenimiento')) DEFAULT 'disponible'
);
INSERT INTO mesas VALUES(1,5,'jardin','reservada');
INSERT INTO mesas VALUES(2,10,'sala central','reservada');
INSERT INTO mesas VALUES(3,11,'terraza','disponible');
INSERT INTO mesas VALUES(4,12,'sala principal','disponible');
CREATE TABLE alimentos (
    id SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL,
    descripcion TEXT,
    tipo_alimento TEXT CHECK (tipo_alimento IN ('entrada', 'plato_fuerte', 'postre', 'bebida')) NOT NULL,
    gramaje INTEGER,
    precio DECIMAL(10,2) NOT NULL,
    estado TEXT CHECK (estado IN ('disponible', 'agotado', 'descontinuado')) DEFAULT 'disponible',
    url_imagen TEXT
);
INSERT INTO alimentos VALUES(1,'Filete Wagyu en Salsa de Trufa Negra','Exquisito corte de carne Wagyu A5 sellado a la perfección, acompañado de reducción de vino tinto y terminado con una delicada salsa de trufa negra. Servido con puré de papas cremoso y espárragos tiernos.','plato_fuerte',100,120000,'disponible','assets/imgs/fileteSalsa.jpg');
INSERT INTO alimentos VALUES(2,'Langosta Thermidor','Langosta fresca gratinada con salsa de vino blanco, mostaza Dijon y queso Gruyère. Servida con un toque de azafrán y vegetales baby salteados en mantequilla.','plato_fuerte',80,150000,'disponible','assets/imgs/plato2.png');
INSERT INTO alimentos VALUES(3,'Tomahawk Dry Aged 45 Días','Imponente corte Tomahawk madurado en seco, sellado en carbón de encina. Acompañado de papas rústicas al romero y salsa chimichurri de la casa.','plato_fuerte',50,150000,'disponible','assets/imgs/plato3.png');
INSERT INTO alimentos VALUES(4,'Lubina al Horno con Cítricos','Lubina fresca horneada lentamente con ralladura de limón, naranja y finas hierbas, servida sobre una cama de risotto de espárragos y mantequilla clarificada.','plato_fuerte',500,140000,'disponible','assets/imgs/plato4.png');
INSERT INTO alimentos VALUES(5,'Ostras Rockefeller','Ostras frescas al horno con espinaca, mantequilla, pan rallado y un toque de Pernod flameado. Un clásico de la alta cocina francesa.','plato_fuerte',20,180000,'disponible','assets/imgs/plato5.png');
INSERT INTO alimentos VALUES(6,'Magret de Pato con Reducción de Oporto','Pechuga de pato cocinada a la perfección, con piel crujiente y jugosa carne rosada. Servida con reducción de vino de Oporto, puré de calabaza y peras caramelizadas.','plato_fuerte',50,170000,'disponible','assets/imgs/plato6.png');
INSERT INTO alimentos VALUES(7,'Hamburguesa de Angus','Hamburguesa con carne angus 100 gr, pan brioche, mix de quesos cremosos de la casa, doble tocineta, tomate dulce y cebolla.','plato_fuerte',100,25000,'disponible','assets/imgs/hamHangus.jpg');
INSERT INTO alimentos VALUES(8,'Pizza con champiñones','Con champiñones, incluye únicamente queso y la salsa de tomate.','plato_fuerte',10,15000,'disponible','assets/imgs/pizzaChampi.jpg');
INSERT INTO alimentos VALUES(9,'La Glotona','Hamburguesa con triple carne artesanal, pan brioche, triple queso cheddar, tocineta, lechuga, tomate, cebolla, pepinillos y salsa de la casa.','plato_fuerte',35,30000,'disponible','assets/imgs/hamGlotona.jpg');
INSERT INTO alimentos VALUES(10,'Perro doble','Hot dog con doble salchicha zenu, pan artesanal, dos huevos de codorniz, queso, jamón, salsas de la casa, cebolla y papitas chip.','plato_fuerte',15,17500,'disponible','assets/imgs/hotDogDouble.jpg');
INSERT INTO alimentos VALUES(11,'Costillas de cerdo al horno','Cosillas de cerdo cocinadas al horno, acompañadas con salsa de la casa, ensalada verde y con papas en cascos.','plato_fuerte',30,30000,'disponible','assets/imgs/costiHorno.jpg');
INSERT INTO alimentos VALUES(12,'Chuletas de cerdo a la plancha','Chuletas bañadas en salsas verdes, acompañadas con papas fritas.','plato_fuerte',35,25000,'disponible','assets/imgs/chulePlancha.jpg');
INSERT INTO alimentos VALUES(13,'Tartar de atún rojo con aguacate y wasabi de castaña','Cubos de atún rojo de primera calidad, marinados ligeramente en salsa de soja y jenjibre, servidos sobre una crema de aguacate, con crujiente galleta de sésamo y un toque de wasabi','entrada',10,35000,'disponible','assets/imgs/tartarAtun.jpg');
INSERT INTO alimentos VALUES(14,'Risotto de azafrán con Foie Gras','Risotto cremoso con azafrán, coronado con perlas de foie gras y laminas de trufa negra','entrada',10,42000,'disponible','assets/imgs/risottoAza.jpg');
INSERT INTO alimentos VALUES(15,'Carpaccio de remolacha y queso de cabra','Laminas de remolacha, helado de albahaca, espuma de cabra y crujientes.','entrada',10,49000,'disponible','assets/imgs/carpaccioRemola.jpg');
INSERT INTO alimentos VALUES(16,'Coca cola','Coca cola personal','bebida',20,5000,'disponible','assets/imgs/cocacola.jpg');
INSERT INTO alimentos VALUES(17,'Seven up','Gaseosa seven up personal','bebida',20,5000,'disponible','assets/imgs/sevenUp.jpg');
INSERT INTO alimentos VALUES(18,'Jugo de mora','Jugo de mora en agua','bebida',20,7000,'disponible','assets/imgs/jugoMora.jpg');
INSERT INTO alimentos VALUES(19,'Jugo de mango','Jugo de mango en agua','bebida',20,7000,'disponible','assets/imgs/jugoMango.jpg');
INSERT INTO alimentos VALUES(20,'Agua de tamarindo','Agua de tamarindo','bebida',20,7000,'disponible','assets/imgs/aguaTamarindo.jpg');
INSERT INTO alimentos VALUES(21,'Coulant de chocolate belga','Bizcocho tibio con corazón fundido de chocolate, acompañado de helado de vainilla de Madagascar y coulis de frutos rojos.','postre',10,25000,'disponible','assets/imgs/coulantChoco.jpg');
INSERT INTO alimentos VALUES(22,'Tiramisú Clásico Italiano','Capas de bizcochos empapados en café espresso, crema de mascarpone y cacao puro espolvoreado.','postre',20,25000,'disponible','assets/imgs/tiramisuClasic.jpg');
INSERT INTO alimentos VALUES(23,'Cheesecake de Frutos Rojos','Tarta de queso cremosa al horno sobre base de galleta, cubierta con mermelada casera de arándanos y frambuesas frescas.','postre',20,28000,'disponible','assets/imgs/cheesecake.jpg');
INSERT INTO alimentos VALUES(24,'Crème Brûlée de Vainilla Bourbon','Crema suave aromatizada con vainilla natural, con una capa de caramelo crocante flameado al momento.','postre',20,35000,'disponible','assets/imgs/cremeBrulee.jpg');
INSERT INTO alimentos VALUES(25,'Mousse de Maracuyá con Crocante de Almendras','Espuma ligera y refrescante de maracuyá, servida sobre base crujiente de almendras caramelizadas.','postre',20,25000,'disponible','assets/imgs/mousseMaracu.jpg');
INSERT INTO alimentos VALUES(26,'Agua','Botella de agua personal','bebida',20,4000,'disponible','assets/imgs/agua.jpg');
INSERT INTO alimentos VALUES(27,'Agua con gas','Botella de agua con gas','bebida',20,5000,'disponible','assets/imgs/aguaGas.jpg');
INSERT INTO alimentos VALUES(28,'Jugo del valle naranja','Botella de jugo del valle sabor naranja','bebida',20,4500,'disponible','assets/imgs/valleNaranja.jpg');
INSERT INTO alimentos VALUES(29,'Jugo del valle mango fresa','Botella personal de jugo del valle de mango y fresa','bebida',200,4500,'disponible','assets/imgs/valleMangoFresa.jpg');
INSERT INTO alimentos VALUES(30,'Jugo del valle salpicon','Botella personal de jugo del valle sabor salpicon','bebida',200,4500,'disponible','assets/imgs/valleSalpicon.jpg');
INSERT INTO alimentos VALUES(31,'Mr Tea','Botella personal de Mr Tea','bebida',200,4500,'disponible','assets/imgs/mrtea.jpg');
INSERT INTO alimentos VALUES(32,'Club colombia roja','Cerveza club colombia roja','bebida',330,8000,'disponible','assets/imgs/clubRoja.jpg');
INSERT INTO alimentos VALUES(33,'Club colombia dorada','Cerveza club colombia dorada','bebida',330,8000,'disponible','assets/imgs/clubAmarila.jpg');
INSERT INTO alimentos VALUES(34,'Club colombia negra','Cerveza club colombia negra','bebida',330,8000,'disponible','assets/imgs/clunNegra.jpg');
CREATE TABLE reservas (
    id SERIAL PRIMARY KEY,
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
INSERT INTO reservas VALUES(1,1,1,'2025-10-01','12:00',3,'cancelada','2025-09-30 00:50:55');
INSERT INTO reservas VALUES(2,1,1,'2025-10-02','12:00',4,'completada','2025-09-30 01:41:50');
INSERT INTO reservas VALUES(3,1,1,'2025-09-30','12:00',5,'cancelada','2025-09-30 01:51:12');
INSERT INTO reservas VALUES(4,1,1,'2025-09-24','12:00',5,'activa','2025-09-30 01:51:53');
INSERT INTO reservas VALUES(5,1,1,'2025-09-23','12:00',4,'activa','2025-09-30 01:56:46');
INSERT INTO reservas VALUES(6,1,1,'2025-09-30','12:00',3,'activa','2025-09-30 01:59:11');
INSERT INTO reservas VALUES(7,1,1,'2025-09-30','12:00',3,'activa','2025-09-30 02:03:40');
INSERT INTO reservas VALUES(8,1,1,'2025-09-09','12:00',4,'activa','2025-09-30 02:06:45');
INSERT INTO reservas VALUES(9,7,1,'2025-10-10','12:00',3,'activa','2025-10-03 22:01:52');
INSERT INTO reservas VALUES(10,7,1,'2025-10-15','12:00',2,'completada','2025-10-03 22:05:41');
INSERT INTO reservas VALUES(11,7,2,'2025-10-15','12:00',3,'completada','2025-10-03 22:11:51');
INSERT INTO reservas VALUES(12,8,1,'2025-10-11','12:00',3,'activa','2025-10-07 15:57:28');
CREATE TABLE pedidos (
    id SERIAL PRIMARY KEY,
    reserva_id INTEGER NOT NULL,
    alimento_id INTEGER NOT NULL,
    cantidad INTEGER NOT NULL CHECK (cantidad > 0),
    estado TEXT CHECK (estado IN ('pendiente', 'en_preparacion', 'listo', 'entregado', 'cancelado')) DEFAULT 'pendiente',
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (reserva_id) REFERENCES reservas(id),
    FOREIGN KEY (alimento_id) REFERENCES alimentos(id)
);
INSERT INTO pedidos VALUES(1,9,15,1,'pendiente','2025-10-03 22:01:52');
INSERT INTO pedidos VALUES(2,9,5,1,'pendiente','2025-10-03 22:01:52');
INSERT INTO pedidos VALUES(3,9,6,1,'pendiente','2025-10-03 22:01:52');
INSERT INTO pedidos VALUES(4,9,7,2,'pendiente','2025-10-03 22:01:52');
INSERT INTO pedidos VALUES(5,9,25,1,'pendiente','2025-10-03 22:01:52');
INSERT INTO pedidos VALUES(6,9,16,2,'pendiente','2025-10-03 22:01:52');
INSERT INTO pedidos VALUES(7,10,13,1,'pendiente','2025-10-03 22:05:41');
INSERT INTO pedidos VALUES(8,11,13,1,'pendiente','2025-10-03 22:11:51');
INSERT INTO pedidos VALUES(9,11,14,2,'pendiente','2025-10-03 22:11:51');
INSERT INTO pedidos VALUES(10,11,15,3,'pendiente','2025-10-03 22:11:51');
INSERT INTO pedidos VALUES(11,11,1,2,'pendiente','2025-10-03 22:11:51');
INSERT INTO pedidos VALUES(12,11,2,3,'pendiente','2025-10-03 22:11:51');
INSERT INTO pedidos VALUES(13,11,3,4,'pendiente','2025-10-03 22:11:51');
INSERT INTO pedidos VALUES(14,11,4,5,'pendiente','2025-10-03 22:11:51');
INSERT INTO pedidos VALUES(15,11,5,6,'pendiente','2025-10-03 22:11:51');
INSERT INTO pedidos VALUES(16,11,6,7,'pendiente','2025-10-03 22:11:51');
INSERT INTO pedidos VALUES(17,11,7,8,'pendiente','2025-10-03 22:11:51');
INSERT INTO pedidos VALUES(18,11,9,9,'pendiente','2025-10-03 22:11:51');
INSERT INTO pedidos VALUES(19,11,16,2,'pendiente','2025-10-03 22:11:51');
INSERT INTO pedidos VALUES(20,12,13,1,'pendiente','2025-10-07 15:57:28');
INSERT INTO pedidos VALUES(21,12,23,1,'pendiente','2025-10-07 15:57:28');
INSERT INTO pedidos VALUES(22,12,20,2,'pendiente','2025-10-07 15:57:28');
INSERT INTO pedidos VALUES(23,12,33,1,'pendiente','2025-10-07 15:57:28');
CREATE TABLE comprobantes (
    id SERIAL PRIMARY KEY,
    reserva_id INTEGER NOT NULL UNIQUE,
    subtotal DECIMAL(10,2) NOT NULL,
    total DECIMAL(10,2) NOT NULL,
    fecha_emision TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (reserva_id) REFERENCES reservas(id)
);
INSERT INTO comprobantes VALUES(1,10,35000,41650,'2025-10-03 22:42:31');
INSERT INTO comprobantes VALUES(2,11,5006000,5957140,'2025-10-03 22:42:58');

CREATE INDEX idx_reservas_cliente ON reservas(cliente_id);
CREATE INDEX idx_reservas_mesa ON reservas(mesa_id);
CREATE INDEX idx_pedidos_reserva ON pedidos(reserva_id);
CREATE INDEX idx_pedidos_alimento ON pedidos(alimento_id);
CREATE INDEX idx_comprobantes_reserva ON comprobantes(reserva_id);
COMMIT;
