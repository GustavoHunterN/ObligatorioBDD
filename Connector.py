import mysql.connector

class Conexion:
    def __init__(self):
        self.cnx = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Luzardo1975!",
            database="OBL"
        )
        self.cursor = self.cnx.cursor(dictionary=True)

    def cerrar(self):
        self.cursor.close()
        self.cnx.close()



