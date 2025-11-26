-- ============================================================
-- Script de Inicialización de Base de Datos - OBL
-- ============================================================
-- Este script crea la base de datos, tablas, usuario y datos iniciales
-- Ejecutar una sola vez al configurar el sistema
-- ============================================================

-- Crear base de datos si no existe
CREATE DATABASE IF NOT EXISTS OBL;
USE OBL;
=========================================================
-- TABLAS
-- ============================================================

-- LOGIN
CREATE TABLE IF NOT EXISTS login(
    correo VARCHAR(255) NOT NULL UNIQUE,
    contrasena VARCHAR(64) NOT NULL
);

-- PARTICIPANTE
CREATE TABLE IF NOT EXISTS participante (
    ci VARCHAR(9) NOT NULL PRIMARY KEY,
    nombre VARCHAR(15) NOT NULL,
    apellido VARCHAR(15) NOT NULL,
    correo VARCHAR(30) NOT NULL UNIQUE,
    rol VARCHAR(10) NOT NULL DEFAULT 'Alumno',
    FOREIGN KEY (correo) REFERENCES login(correo)
);

-- SANCION
CREATE TABLE IF NOT EXISTS sancion_participante(
    id_sancion INT PRIMARY KEY AUTO_INCREMENT,
    ci VARCHAR(9) NOT NULL,
    fecha_inicio DATETIME NOT NULL,
    fecha_final DATETIME,
    FOREIGN KEY (ci) REFERENCES participante(ci)
);

-- FACULTAD
CREATE TABLE IF NOT EXISTS facultad(
    nombre VARCHAR(30) PRIMARY KEY UNIQUE
);

-- PROGRAMA ACADEMICO
CREATE TABLE IF NOT EXISTS programa_academico(
    nombre_programa VARCHAR(30) NOT NULL PRIMARY KEY,
    nombre_facultad VARCHAR(30) NOT NULL,
    tipo VARCHAR(10),
    FOREIGN KEY (nombre_facultad) REFERENCES facultad(nombre)
);

-- PARTICIPANTE_PROGRAMA
CREATE TABLE IF NOT EXISTS participante_programa(
    id_part_prog INT PRIMARY KEY AUTO_INCREMENT,
    rol VARCHAR(20) NOT NULL,
    nombre_programa VARCHAR(30),
    ci VARCHAR(9) NOT NULL,
    FOREIGN KEY (nombre_programa) REFERENCES programa_academico(nombre_programa),
    FOREIGN KEY (ci) REFERENCES participante(ci)
);

-- EDIFICIO
CREATE TABLE IF NOT EXISTS edificio(
    nombre_edificio VARCHAR(15) NOT NULL PRIMARY KEY,
    direccion VARCHAR(30),
    departamento VARCHAR(10)
);

-- SALA
CREATE TABLE IF NOT EXISTS sala(
    nombre_sala VARCHAR(5) NOT NULL PRIMARY KEY,
    capacidad INT NOT NULL,
    tipo_sala VARCHAR(8),
    edificio VARCHAR(15) NOT NULL,
    FOREIGN KEY (edificio) REFERENCES edificio(nombre_edificio)
);

-- TURNOS
CREATE TABLE IF NOT EXISTS turnos(
    id_turno INT PRIMARY KEY AUTO_INCREMENT,
    hora_inicio TIME,
    hora_final TIME
);

-- RESERVA
CREATE TABLE IF NOT EXISTS reserva(
    id_reserva INT PRIMARY KEY AUTO_INCREMENT,
    fecha DATE NOT NULL,
    estado VARCHAR(14) NOT NULL,
    id_turno INT NOT NULL,
    nombre_edificio VARCHAR(15) NOT NULL,
    sala VARCHAR(5) NOT NULL,
    FOREIGN KEY (nombre_edificio) REFERENCES edificio(nombre_edificio),
    FOREIGN KEY (id_turno) REFERENCES turnos(id_turno),
    FOREIGN KEY (sala) REFERENCES sala(nombre_sala)
);

-- RESERVA_PARTICIPANTE
CREATE TABLE IF NOT EXISTS reserva_participante (
    id_reserva_part INT PRIMARY KEY AUTO_INCREMENT,
    ci VARCHAR(9) NOT NULL,
    id_reserva INT NOT NULL,
    fecha_solicitud DATETIME,
    asistencia TINYINT(1),
    FOREIGN KEY (id_reserva) REFERENCES reserva(id_reserva),
    FOREIGN KEY (ci) REFERENCES participante(ci)
);

-- ============================================================
-- DATOS INICIALES
-- ============================================================

-- Insertar turnos (horarios de 8:00 a 22:00, cada hora)
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
('21:00:00', '22:00:00')
ON DUPLICATE KEY UPDATE hora_inicio = hora_inicio;

-- ============================================================
-- USUARIO DE APLICACIÓN
-- ============================================================

-- Crear usuario de aplicación con privilegios mínimos
CREATE USER IF NOT EXISTS 'appuser'@'%' IDENTIFIED BY 'securepassword';

-- Otorgar privilegios necesarios
GRANT SELECT, INSERT, UPDATE, DELETE ON OBL.* TO 'appuser'@'%';

-- Aplicar cambios
FLUSH PRIVILEGES;
