import mysql.connector
import os

class Conexion:
    def __init__(self):
        """
        Conexión a base de datos usando usuario con privilegios mínimos.
        
        Las credenciales se cargan desde variables de entorno por seguridad.
        Valores por defecto para desarrollo con Docker.
        
        Variables de entorno:
        - DB_USER: Usuario de base de datos (por defecto: 'appuser')
        - DB_PASSWORD: Contraseña de base de datos (por defecto: 'securepassword')
        - DB_HOST: Host de base de datos (por defecto: 'db' para Docker, 'localhost' para local)
        - DB_NAME: Nombre de base de datos (por defecto: 'OBL')
        """
        # Cargar credenciales desde variables de entorno (seguro)
        # Valores por defecto para desarrollo con Docker
        db_user = os.getenv('DB_USER', 'appuser')
        db_password = os.getenv('DB_PASSWORD', 'securepassword')
        db_host = os.getenv('DB_HOST', 'db')  # 'db' es el nombre del servicio en docker-compose
        db_name = os.getenv('DB_NAME', 'OBL')
        
        self.cnx = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name
        )
        self.cursor = self.cnx.cursor(dictionary=True)

    def cerrar(self):
        self.cursor.close()
        self.cnx.close()



