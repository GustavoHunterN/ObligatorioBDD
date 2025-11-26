"""
Script para cargar datos iniciales de prueba.
Se ejecuta automáticamente al iniciar la aplicación.
"""
from Connector import Conexion

def cargar_datos_prueba():
    """Cargar datos mínimos de prueba si no existen."""
    conexion = Conexion()
    
    try:
        # Verificar si ya existen datos de prueba (verificamos si existe el docente de prueba)
        conexion.cursor.execute("""
            SELECT ci FROM participante WHERE ci = '1234567D'
        """)
        datos_existen = conexion.cursor.fetchone()
        
        if datos_existen:
            print("✅ Los datos de prueba ya están cargados.")
            conexion.cerrar()
            return
        
        print("📦 Cargando datos de prueba...")
        
        # LOGIN
        conexion.cursor.execute("""
            INSERT IGNORE INTO login (correo, contrasena) VALUES
            ('juan.perez@docente.com', 'docente123'),
            ('maria.garcia@alumno.com', 'alumno123'),
            ('carlos.lopez@alumno.com', 'alumno456')
        """)
        
        # PARTICIPANTES
        conexion.cursor.execute("""
            INSERT IGNORE INTO participante (ci, nombre, apellido, correo, rol) VALUES
            ('1234567D', 'Juan', 'Perez', 'juan.perez@docente.com', 'Docente'),
            ('1111111A', 'Maria', 'Garcia', 'maria.garcia@alumno.com', 'Alumno'),
            ('2222222A', 'Carlos', 'Lopez', 'carlos.lopez@alumno.com', 'Alumno')
        """)
        
        # FACULTADES
        conexion.cursor.execute("""
            INSERT IGNORE INTO facultad (nombre) VALUES
            ('Ingenieria'),
            ('Ciencias')
        """)
        
        # PROGRAMAS ACADÉMICOS
        conexion.cursor.execute("""
            INSERT IGNORE INTO programa_academico (nombre_programa, nombre_facultad, tipo) VALUES
            ('Ingenieria Informatica', 'Ingenieria', 'Grado'),
            ('Matematicas', 'Ciencias', 'Posgrado')
        """)
        
        # PARTICIPANTE_PROGRAMA
        conexion.cursor.execute("""
            INSERT IGNORE INTO participante_programa (rol, nombre_programa, ci) VALUES
            ('Docente', 'Ingenieria Informatica', '1234567D'),
            ('Alumno', 'Ingenieria Informatica', '1111111A'),
            ('Alumno', 'Ingenieria Informatica', '2222222A'),
            ('Alumno', 'Matematicas', '1111111A')
        """)
        
        # EDIFICIOS
        conexion.cursor.execute("""
            INSERT IGNORE INTO edificio (nombre_edificio, direccion, departamento) VALUES
            ('A', 'Av. Principal 123', 'Montevideo'),
            ('B', 'Calle Secundaria 456', 'Montevideo')
        """)
        
        # SALAS
        conexion.cursor.execute("""
            INSERT IGNORE INTO sala (nombre_sala, capacidad, tipo_sala, edificio) VALUES
            ('A001', 30, 'Libre', 'A'),
            ('A002', 25, 'Docente', 'A'),
            ('A003', 40, 'Posgrado', 'A'),
            ('B001', 50, 'Libre', 'B')
        """)
        
        conexion.cnx.commit()
        conexion.cerrar()
        
        print("✅ Datos de prueba cargados correctamente.")
        print("\n📋 Credenciales disponibles:")
        print("   Docente: juan.perez@docente.com / docente123")
        print("   Alumno 1: maria.garcia@alumno.com / alumno123")
        print("   Alumno 2: carlos.lopez@alumno.com / alumno456")
        
    except Exception as e:
        conexion.cerrar()
        print(f"⚠️  Error al cargar datos de prueba: {e}")
        print("   (Esto no impide que la aplicación funcione)")

if __name__ == "__main__":
    print("🔧 Cargando datos de prueba...\n")
    cargar_datos_prueba()

