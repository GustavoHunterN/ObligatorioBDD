-- ============================================================
-- Remove Excessive Privileges (if user already exists)
-- ============================================================
-- Run this script if you need to revoke excessive privileges
-- from an existing user.
-- ============================================================

-- Revoke all privileges first (if user has excessive privileges)
REVOKE ALL PRIVILEGES, GRANT OPTION FROM 'appuser'@'localhost';

-- Then grant only the necessary privileges (same as create_app_user.sql)
GRANT SELECT, INSERT, UPDATE, DELETE ON OBL.login TO 'appuser'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON OBL.participante TO 'appuser'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON OBL.sancion_participante TO 'appuser'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON OBL.facultad TO 'appuser'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON OBL.programa_academico TO 'appuser'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON OBL.participante_programa TO 'appuser'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON OBL.edificio TO 'appuser'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON OBL.sala TO 'appuser'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON OBL.turnos TO 'appuser'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON OBL.reserva TO 'appuser'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON OBL.reserva_participante TO 'appuser'@'localhost';

-- Apply changes
FLUSH PRIVILEGES;

