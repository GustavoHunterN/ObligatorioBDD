"""
Script para crear la cuenta de administrador inicial.
Ejecutar una vez para configurar el primer usuario administrador.
"""
from Connector import Conexion

def create_admin_account():
    """Crear la cuenta de administrador por defecto si no existe."""
    conexion = Conexion()
    
    try:
        # Verificar si el admin ya existe
        conexion.cursor.execute("""
            SELECT ci FROM participante WHERE ci = '000ADMIN'
        """)
        existing = conexion.cursor.fetchone()
        
        if existing:
            print("✅ ¡La cuenta de administrador ya existe!")
            print("   Email: admin@admin.com")
            print("   Contraseña: admin123")
            conexion.cerrar()
            return
        
        # Crear entrada de login
        conexion.cursor.execute("""
            INSERT INTO login (correo, contrasena)
            VALUES ('admin@admin.com', 'admin123')
        """)
        
        # Crear participante admin
        conexion.cursor.execute("""
            INSERT INTO participante (ci, nombre, apellido, correo, rol)
            VALUES ('000ADMIN', 'Admin', 'General', 'admin@admin.com', 'Admin')
        """)
        
        conexion.cnx.commit()
        conexion.cerrar()
        
        print("✅ ¡Cuenta de administrador creada exitosamente!")
        print("\n📋 Credenciales de acceso:")
        print("   Email: admin@admin.com")
        print("   Contraseña: admin123")
        print("\n⚠️  IMPORTANTE: Cambiar la contraseña después del primer inicio de sesión!")
        print("\n🔗 Acceder al panel de administrador en: http://localhost:5000")
        print("   (El admin puede iniciar sesión desde cualquier formulario de login)")
        
    except Exception as e:
        conexion.cerrar()
        print(f"❌ Error al crear la cuenta de administrador: {e}")
        print("\nPosibles causas:")
        print("  - Fallo en la conexión a la base de datos")
        print("  - Las tablas no existen (ejecutar DB/init.sql primero)")
        print("  - La cuenta de admin ya existe con credenciales diferentes")

if __name__ == "__main__":
    print("🔧 Configurando cuenta de administrador inicial...\n")
    create_admin_account()

