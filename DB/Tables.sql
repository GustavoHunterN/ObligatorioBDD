USE OBL;
-- LOGIN ----------------------------------------------------
CREATE TABLE login(
    correo VARCHAR(255) NOT NULL UNIQUE,
    contraseña VARCHAR (64) NOT NULL
);

-- PARTICIPANTE ---------------------------------------------
CREATE TABLE participante (
    ci VARCHAR(8) NOT NULL PRIMARY KEY,
    nombre VARCHAR(15) NOT NULL,
    apellido VARCHAR(15) NOT NULL,
    correo VARCHAR(30) NOT NULL UNIQUE,
    FOREIGN KEY (correo) REFERENCES login(correo)
);

-- SANCION ---------------------------------------------------
CREATE TABLE sancion_participante(
    id_sancion INT PRIMARY KEY AUTO_INCREMENT,
    ci VARCHAR(8) NOT NULL,
    fecha_inicio DATETIME NOT NULL,
    fecha_final DATETIME,
    FOREIGN KEY (ci) REFERENCES participante(ci)
);

-- FACULTAD --------------------------------------------------
CREATE TABLE facultad(
    id_facultad VARCHAR(6) NOT NULL PRIMARY KEY,
    nombre VARCHAR(15)
);

-- PROGRAMA --------------------------------------------------
CREATE TABLE programa_academico(
    nombre_programa VARCHAR(20) NOT NULL PRIMARY KEY,
    id_facultad VARCHAR(6) NOT NULL,
    tipo VARCHAR(8),
    FOREIGN KEY (id_facultad) REFERENCES facultad(id_facultad)
);

-- PARTICIPANTE_PROGRAMA -------------------------------------
CREATE TABLE participante_programa(
    id_part_prog INT PRIMARY KEY AUTO_INCREMENT,
    rol VARCHAR(20) NOT NULL,
    nombre_programa VARCHAR(20),
    ci VARCHAR(8) NOT NULL,
    FOREIGN KEY (nombre_programa) REFERENCES programa_academico(nombre_programa),
    FOREIGN KEY (ci) REFERENCES participante(ci)
);

-- EDIFICIO ---------------------------------------------------
CREATE TABLE edificio(
    nombre_edificio VARCHAR(15) NOT NULL PRIMARY KEY,
    direccion VARCHAR(30),
    departamento VARCHAR(10)
);
-- SALA -------------------------------------------------------
CREATE TABLE sala(
    nombre_sala VARCHAR(5) NOT NULL PRIMARY KEY,
    capacidad INT NOT NULL,
    tipo_sala VARCHAR(8),
    edificio VARCHAR(15) NOT NULL,
    FOREIGN KEY (edificio) REFERENCES edificio(nombre_edificio)
);

-- TURNOS -----------------------------------------------------
CREATE TABLE turnos(
    id_turno INT PRIMARY KEY AUTO_INCREMENT,
    hora_inicio TIME,
    hora_final TIME
);


-- RESERVA ----------------------------------------------------
CREATE TABLE reserva(
    id_reserva INT PRIMARY KEY AUTO_INCREMENT,
    fecha DATETIME,
    estado VARCHAR(14) NOT NULL,
    id_turno INT NOT NULL,
    nombre_edificio VARCHAR(15) NOT NULL,
    sala VARCHAR(5) NOT NULL,
    FOREIGN KEY (nombre_edificio) REFERENCES edificio(nombre_edificio),
    FOREIGN KEY (id_turno) REFERENCES turnos(id_turno),
    FOREIGN KEY (sala) REFERENCES sala(nombre_sala)
);

-- RESERVA_PARTICIPANTE ---------------------------------------
CREATE TABLE reserva_participante (
    id_reserva_part INT PRIMARY KEY AUTO_INCREMENT,
    ci VARCHAR(8) NOT NULL,
    id_reserva INT NOT NULL,
    fecha_solicitud DATETIME,
    asistencia TINYINT(1),
    FOREIGN KEY (id_reserva) REFERENCES reserva(id_reserva),
    FOREIGN KEY (ci) REFERENCES participante(ci)
);

INSERT INTO turnos (hora_inicio, hora_final) VALUES
('08:00:00', '09:00:00'),
('09:00:00', '10:00:00'),
('10:00:00', '11:00:00'),
('11:00:00', '12:00:00'),
('12:00:00', '13:00:00'),
('13:00:00', '14:00:00'),
('14:00:00', '15:00:00'),
('15:00:00', '16:00:00'),
('16:00:00', '17:00:00'),
('17:00:00', '18:00:00'),
('18:00:00', '19:00:00'),
('19:00:00', '20:00:00'),
('20:00:00', '21:00:00'),
('21:00:00', '22:00:00');



DESCRIBE edificio;
DESCRIBE sala;
DESCRIBE turnos;
DESCRIBE reserva;


SELECT * FROM sala

SELECT * FROM reserva


describe reserva

