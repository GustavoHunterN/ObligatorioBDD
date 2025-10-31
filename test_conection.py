from Connector import Conexion


db = Conexion()
db.cursor.execute('SHOW TABLES')
tablas = db.cursor.fetchall()
print([t for t in tablas])