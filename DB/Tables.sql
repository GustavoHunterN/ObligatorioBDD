USE OBL;
-- LOGIN ----------------------------------------------------
CREATE TABLE login(
    correo VARCHAR(255) NOT NULL UNIQUE,
    contrasena VARCHAR (64) NOT NULL
);

-- PARTICIPANTE ---------------------------------------------
CREATE TABLE participante (
    ci VARCHAR(9) NOT NULL PRIMARY KEY,
    nombre VARCHAR(15) NOT NULL,
    apellido VARCHAR(15) NOT NULL,
    correo VARCHAR(30) NOT NULL UNIQUE,
    rol VARCHAR(10) NOT NULL DEFAULT 'Alumno',
    FOREIGN KEY (correo) REFERENCES login(correo)
);

-- SANCION ---------------------------------------------------
CREATE TABLE sancion_participante(
    id_sancion INT PRIMARY KEY AUTO_INCREMENT,
    ci VARCHAR(9) NOT NULL,
    fecha_inicio DATETIME NOT NULL,
    fecha_final DATETIME,
    FOREIGN KEY (ci) REFERENCES participante(ci)
);

-- FACULTAD --------------------------------------------------
CREATE TABLE facultad(
    nombre VARCHAR(15) PRIMARY KEY UNIQUE
);

-- PROGRAMA --------------------------------------------------
CREATE TABLE programa_academico(
    nombre_programa VARCHAR(30) NOT NULL PRIMARY KEY,
    nombre_facultad VARCHAR(30) NOT NULL,
    tipo VARCHAR(8),
    FOREIGN KEY (nombre_facultad) REFERENCES facultad(nombre)
);

-- PARTICIPANTE_PROGRAMA -------------------------------------
CREATE TABLE participante_programa(
    id_part_prog INT PRIMARY KEY AUTO_INCREMENT,
    rol VARCHAR(20) NOT NULL,
    nombre_programa VARCHAR(30),
    ci VARCHAR(9) NOT NULL,
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
    ci VARCHAR(9) NOT NULL,
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



SELECT * FROM reserva;
SELECT * FROM participante;
SELECT * FROM participante_programa;
SELECT * FROM login;
SELECT * FROM edificio;
SELECT * FROM facultad;
SELECT * FROM programa_academico;
SELECT * FROM turnos;
SELECT * FROM sala;
SELECT * FROM reserva_participante rp
    JOIN reserva r WHERE r.id_reserva = rp.id_reserva
SELECT * FROM sancion_participante
JOIN participante WHERE participante.ci = sancion_participante.ci;


DROP TABLE login;

INSERT INTO participante_programa( rol, nombre_programa, ci) VALUES ('Alumno','a','58898A')

;
SELECT
            p.ci,
            p.nombre,
            p.apellido,
            p.correo,
            pp.rol AS rol_programa,
            pp.nombre_programa,
            pr.tipo AS tipo_programa
        FROM participante p
        JOIN login l ON l.correo = p.correo
        JOIN participante_programa pp ON pp.ci = p.ci
        JOIN programa_academico pr ON pr.nombre_programa = pp.nombre_programa
        WHERE l.correo = 'c@m.com'
          AND l.contrasena = ' '
          AND pp.rol = 'Alumno'
        LIMIT 1;

        SELECT *
        FROM participante p
        JOIN login l ON l.correo = p.correo;



describe reserva;
DELETE FROM facultad
WHERE nombre = 'Derecho';

DELETE FROM participante_programa
WHERE id_part_prog = 8
DELETE FROM participante_programa
WHERE id_part_prog = 10
;
INSERT INTO sala(nombre_sala, capacidad, tipo_sala, edificio) VALUES ('M001', 40, 'Posgrado', 'Mullin')
ALTER TABLE participante
CHANGE COLUMN `ci` `ci` VARCHAR(9);


ALTER TABLE programa_academico
CHANGE COLUMN `nombre_facultad` `nombre_facultad` VARCHAR(30);

ALTER TABLE facultad
CHANGE COLUMN `nombre` `nombre` VARCHAR(30);

ALTER TABLE programa_academico
CHANGE COLUMN `tipo` `tipo` VARCHAR(10);

ALTER TABLE reserva_participante
CHANGE COLUMN `ci` `ci` VARCHAR(9);

ALTER TABLE participante_programa
CHANGE COLUMN `nombre_programa` `nombre_programa` VARCHAR(30);

describe programa_academico;

DROP DATABASE OBL;
CREATE DATABASE OBL;
USE OBL;

SELECT CONCAT('[', nombre_edificio, ']')
FROM edificio;

INSERT INTO facultad (nombre)
VALUES ('FacuTest');
INSERT INTO programa_academico
VALUES ('coso2', 'FacuTest', 'Grado');
INSERT INTO participante_programa (rol, nombre_programa, ci )
VALUES ('Alumno', 'coso', '58898A');
INSERT INTO edificio (nombre_edificio, direccion, departamento)
VALUES ('Ed1', 'Calle Falsa 123', 'Montevideo');
INSERT INTO sala (nombre_sala, capacidad, tipo_sala, edificio)
VALUES ('P01A', 30, 'Grado', 'Ed1');
INSERT INTO sala (nombre_sala, capacidad, tipo_sala, edificio)
VALUES ('P01B', 30, 'Docente', 'Ed1');

select * from reserva_participante
SELECT l.correo, contrasena,pp.rol , pp.nombre_programa, pa.tipo FROM login l
JOIN participante p ON l.correo = p.correo
JOIN participante_programa pp ON p.ci = pp.ci
JOIN programa_academico pa ON pa.nombre_programa = pp.nombre_programa

SELECT * FROM participante
JOIN login ON participante.correo = login.correo



ALTER TABLE participante
ADD COLUMN rol VARCHAR(10) NOT NULL DEFAULT 'Alumno';
SELECT p.ci, p.nombre, p.apellido, pp.nombre_programa
FROM participante_programa pp
JOIN participante p ON p.ci = pp.ci
WHERE pp.nombre_programa = 'a'


SELECT edificio
FROM sala
WHERE nombre_sala = 'P002'


INSERT INTO participante (ci, nombre, apellido, correo,  rol)
VALUES ('000ADMIN', 'Admin', 'General', 'admin@admin.com', 'Admin');
INSERT INTO login (correo, contrasena)
VALUES ('admin@admin.com', 'admin123');
