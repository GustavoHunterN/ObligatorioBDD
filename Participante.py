class Participante:
    def __init__(self, ci, nombre, apellido, correo, contrasena):
        self.ci = ci
        self.nombre = nombre
        self.apellido = apellido
        self.correo = correo
        self.contrasena = contrasena
        self.sanciones = []

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.ci}) — {self.correo}"

    def __repr__(self):
        return (f"Participante(ci={self.ci!r}, nombre={self.nombre!r}, "
                f"apellido={self.apellido!r}, correo={self.correo!r})")

    def save(self, conexion):
        query_login = "INSERT INTO login (correo, contrasena) VALUES (%s, %s);"
        query_part = """
        INSERT INTO participante (ci, nombre, apellido, correo)
        VALUES (%s, %s, %s, %s);
        """
        conexion.cursor.execute(query_login, (self.correo, self.contrasena))
        conexion.cursor.execute(query_part, (self.ci, self.nombre, self.apellido, self.correo))
        conexion.cnx.commit()

    def load_all(self, conexion):
        query = """
        SELECT * FROM participante
        """
        conexion.cursor.execute(query)
        resultado = conexion.cursor.fetchall()
        return resultado


class Alumno(Participante):
    def __init__(self, ci, nombre, apellido):
        self.ci  = f'{ci}A'
        self.nombre = f'{nombre[0].upper()+nombre[1:].lower()}'
        self.apellido = f'{apellido[0].upper()+apellido[1:].lower()}'
        self.correo = f"{self.nombre}.{self.apellido}@alumno.com"
        self.contrasena = " "
        super().__init__(self.ci, self.nombre, self.apellido, self.correo, self.contrasena)

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.ci}) — {self.correo}"

    def __repr__(self):
        return (f"Alumno(ci={self.ci!r}, nombre={self.nombre!r}, "
                f"apellido={self.apellido!r}, correo={self.correo!r})")


class Docente(Participante):
    def __init__(self, ci, nombre, apellido):
        self.ci  = f'{ci}D'
        self.nombre = f'{nombre[0].upper()+nombre[1:].lower()}'
        self.apellido = f'{apellido[0].upper()+apellido[1:].lower()}'
        self.correo = f"{self.nombre}.{self.apellido}@docente.com"
        self.contrasena = " "
        super().__init__(self.ci, self.nombre, self.apellido, self.correo, self.contrasena)

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.ci}) — {self.correo}"

    def __repr__(self):
        return (f"Docente(ci={self.ci!r}, nombre={self.nombre!r}, "
                f"apellido={self.apellido!r}, correo={self.correo!r})")






