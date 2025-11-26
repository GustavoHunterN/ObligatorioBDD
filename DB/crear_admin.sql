-- ============================================================
-- Script para crear cuenta de administrador inicial
-- ============================================================
-- Ejecutar después de crear las tablas
-- ============================================================

USE OBL;

-- Crear cuenta de login para admin
INSERT IGNORE INTO login (correo, contrasena)
VALUES ('admin@admin.com', 'admin123');

-- Crear participante admin
INSERT IGNORE INTO participante (ci, nombre, apellido, correo, rol)
VALUES ('000ADMIN', 'Admin', 'General', 'admin@admin.com', 'Admin');

