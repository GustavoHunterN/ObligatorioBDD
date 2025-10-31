shUSE OBL;

CREATE TABLE login(
    correo VARCHAR(255) NOT NULL UNIQUE,
    contraseña VARCHAR (64) NOT NULL
);



CREATE TABLE participante (
    ci VARCHAR(8) NOT NULL UNIQUE PRIMARY KEY,
    nombre VARCHAR(15) NOT NULL,
    apellido VARCHAR(15) NOT NULL,
    correo VARCHAR(30) NOT NULL UNIQUE,
    FOREIGN KEY (correo) REFERENCES login(correo)
);


CREATE TABLE sancion_participante(
    ci VARCHAR(8) NOT NULL UNIQUE,
    fecha_inicio DATETIME NOT NULL,
    fecha_final DATETIME,
    FOREIGN KEY (ci) REFERENCES participante(ci)
);

CREATE TABLE facultad(
    id_facultad VARCHAR(6) NOT NULL UNIQUE,
    nombre VARCHAR(15)
);



CREATE TABLE programa_academico(
    nombre_programa VARCHAR(20) NOT NULL UNIQUE PRIMARY KEY,
    id_facultad VARCHAR(6) NOT NULL UNIQUE,
    tipo VARCHAR(8),
    FOREIGN KEY (id_facultad) REFERENCES facultad(id_facultad)
                               );


CREATE TABLE participante_programa(
    id_part_prog INT PRIMARY KEY AUTO_INCREMENT,
    rol VARCHAR(20) NOT NULL,
    nombre_programa VARCHAR(50),
    ci VARCHAR(8) NOT NULL UNIQUE,
    FOREIGN KEY (nombre_programa) REFERENCES programa_academico(nombre_programa),
    FOREIGN KEY (ci) REFERENCES participante(ci)
);


CREATE TABLE edificio(
    direccion VARCHAR(30),
    departamento VARCHAR(10),
    nombre_edif VARCHAR(15) NOT NULL UNIQUE
);

CREATE TABLE turnos(
    id_turno INT PRIMARY KEY AUTO_INCREMENT,
    hora_inicio TIME,
    hora_final TIME
);

CREATE TABLE sala(
    nombre_sala VARCHAR(5) NOT NULL UNIQUE,
    capacidad INT NOT NULL,
    tipo_sala VARCHAR(8),
    edificio  VARCHAR(15) NOT NULL,
    FOREIGN KEY (edificio) REFERENCES edificio(nombre_edif)
);
CREATE TABLE reserva(
    id_reserva INT PRIMARY KEY AUTO_INCREMENT,
    fecha DATETIME,
    estado VARCHAR(14) NOT NULL,
    id_turno INT NOT NULL,
    nombre_edificio VARCHAR(15) NOT NULL,
    sala  VARCHAR(5) NOT NULL,
    FOREIGN KEY (nombre_edificio) REFERENCES edificio(nombre_edif),
    FOREIGN KEY (id_turno) REFERENCES turnos(id_turno),
    FOREIGN KEY (sala) REFERENCES sala(nombre_sala)
);

CREATE TABLE reserva_participante (
    ci VARCHAR(8) NOT NULL UNIQUE PRIMARY KEY,
    id_reserva INT NOT NULL,
    fecha_solicitud DATETIME,
    asistencia TINYINT(1),
    FOREIGN KEY (id_reserva) REFERENCES reserva(id_reserva),
    FOREIGN KEY (ci) REFERENCES participante(ci)
);