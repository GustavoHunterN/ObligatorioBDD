-- ============================================================
-- Database Security: Least-Privilege User Creation
-- ============================================================
-- This script creates a dedicated MySQL user with minimal
-- privileges required for the OBL application.
-- ============================================================

-- Step 1: Create the application user
-- Replace 'securepassword' with a strong password in production
CREATE USER IF NOT EXISTS 'appuser'@'localhost' IDENTIFIED BY 'securepassword';

-- Step 2: Grant only necessary privileges on OBL database
-- SELECT: Required for all read operations (queries, lookups, reports)
-- INSERT: Required for creating new records
-- UPDATE: Required for modifying existing records
-- DELETE: Required for removing records

-- Grant privileges on all tables
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

-- Step 3: Apply the changes
FLUSH PRIVILEGES;

-- Step 4: Verify privileges (optional - run as root)
-- SHOW GRANTS FOR 'appuser'@'localhost';

-- ============================================================
-- Security Notes:
-- ============================================================
-- 1. This user CANNOT:
--    - Create/drop databases or tables (CREATE/DROP)
--    - Modify table structure (ALTER)
--    - Truncate tables (TRUNCATE)
--    - Manage users or privileges (GRANT/REVOKE)
--    - Access other databases
--    - Execute file operations (FILE privilege)
--    - Lock tables (LOCK TABLES)
--
-- 2. This user CAN:
--    - Read data (SELECT)
--    - Insert new records (INSERT)
--    - Update existing records (UPDATE)
--    - Delete records (DELETE)
--
-- 3. In production:
--    - Change 'securepassword' to a strong, unique password
--    - Store credentials securely (environment variables, secrets manager)
--    - Consider using SSL/TLS for connections
--    - Regularly audit user privileges
-- ============================================================

