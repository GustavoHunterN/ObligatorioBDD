import Connector as C

con = C.Conexion()

print(con.cursor.execute("USE OBL;"))
print(con.cursor.execute("SELECT * FROM TABLES;"))



