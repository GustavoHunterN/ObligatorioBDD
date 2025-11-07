class Edificio:
    def __init__(self, nombre, direccion, departamento):
        self.nombre = nombre
        self.direccion = direccion
        self.departamento = departamento

    
    def __str__(self):
        return f"Edificio: {self.nombre} — Dirección: {self.direccion}, Depto: {self.departamento}"

    
    def __repr__(self):
        return f"Edificio(nombre={self.nombre!r}, direccion={self.direccion!r}, departamento={self.departamento!r})"

    def save(self, conexion):
        query = """
        INSERT INTO edificio (nombre_edificio, direccion, departamento)
        VALUES (%s, %s, %s);
        """
        conexion.cursor.execute(query, (self.nombre, self.direccion, self.departamento))
        conexion.cnx.commit()

    def load_all(self, conexion):
        query = """
        SELECT * FROM edificio
        """
        conexion.cursor.execute(query)
        resultado = conexion.cursor.fetchall()
        return resultado



class Sala:

    def __init__(self, nombre, capacidad, edificio, tipo):
        self.nombre = nombre
        self.capacidad = capacidad
        self.edificio = edificio
        self.tipo_sala = tipo

    
    def __str__(self):
        return f"Sala: {self.nombre} — Capacidad: {self.capacidad} — Tipo: {self.tipo_sala} — Edificio: {self.edificio.nombre}"

    
    def __repr__(self):
        return (f"Sala(nombre={self.nombre!r}, capacidad={self.capacidad!r}, "
                f"edificio={self.edificio!r}, tipo_sala={self.tipo_sala!r})")

    def validar_edificio(self):
        if not isinstance(self.edificio, Edificio):
            raise TypeError("El edificio debe ser de tipo Edificio")

    def set_nombre(self, num):
        self.nombre = str(self.edificio.nombre[0].upper() + "0" + num)

    def save(self, conexion):
        query = """
        INSERT INTO sala (nombre_sala, capacidad, tipo_sala, edificio)
        VALUES (%s, %s, %s, %s);
        """
        conexion.cursor.execute(query, (self.nombre, self.capacidad, self.tipo_sala, self.edificio.nombre))
        conexion.cnx.commit()

    def load_all(self, conexion):
        query = """
        SELECT * FROM sala
        """
        conexion.cursor.execute(query)
        resultado = conexion.cursor.fetchall()
        return resultado


class Turnos:
    def __init__(self, hora_inicio, hora_final, dia, sala):
        self.hora_inicio = hora_inicio
        self.hora_final = hora_final
        self.dia = dia
        self.sala = sala          # instancia de Sala
        self.id_turno = None

    
    def __str__(self):
        return f"Turno #{self.id_turno or '—'} — {self.dia} {self.hora_inicio}-{self.hora_final} — Sala: {self.sala.nombre}"

    
    def __repr__(self):
        return (f"Turnos(id_turno={self.id_turno!r}, hora_inicio={self.hora_inicio!r}, "
                f"hora_final={self.hora_final!r}, dia={self.dia!r}, sala={self.sala!r})")

    def validar_sala(self):
        if not isinstance(self.sala, Sala):
            raise TypeError("La sala debe ser de tipo Sala")

    def save(self, conexion):
        query = """
        INSERT INTO turnos (hora_inicio, hora_final, dia, nombre_sala)
        VALUES (%s, %s, %s, %s);
        """
        conexion.cursor.execute(query, (self.hora_inicio, self.hora_final, self.dia, self.sala.nombre))
        self.id_turno = conexion.cursor.lastrowid  
        conexion.cnx.commit()

    def load_all(self, conexion):
        query = """
        SELECT * FROM turnos
        """
        conexion.cursor.execute(query)
        resultado = conexion.cursor.fetchall()
        return resultado

class Reserva:
    # [MOD] id lo maneja la DB (AUTO_INCREMENT). Guardamos id_reserva tras save()
    def __init__(self, sala, turno, estado, fecha):
        self.sala = sala              # instancia Sala
        self.edificio = sala.edificio # cache útil
        self.turno = turno            # instancia Turnos (con id_turno)
        self.estado = estado
        self.fecha = fecha
        self.id_reserva = None

    
    def __str__(self):
        return (f"Reserva #{self.id_reserva or '—'}: {self.sala.nombre} en {self.edificio.nombre} "
                f"({self.estado}) — {self.fecha}")

    
    def __repr__(self):
        return (f"Reserva(id_reserva={self.id_reserva!r}, sala={self.sala!r}, edificio={self.edificio!r}, "
                f"turno={self.turno!r}, estado={self.estado!r}, fecha={self.fecha!r})")

    def validar_sala(self):
        if not isinstance(self.sala, Sala):
            raise TypeError("La sala debe ser de tipo Sala")

    def validar_turno(self):
        if not isinstance(self.turno, Turnos):
            raise TypeError("El turno debe ser de tipo Turnos")

    def save(self, conexion):
        if self.turno.id_turno is None:
            raise ValueError("Turnos.save() debe llamarse antes para obtener id_turno")
        query = """
        INSERT INTO reserva (fecha, estado, id_turno, nombre_edificio, sala)
        VALUES (%s, %s, %s, %s, %s);
        """
        conexion.cursor.execute(query, (self.fecha, self.estado, self.turno.id_turno, self.edificio.nombre, self.sala.nombre))
        self.id_reserva = conexion.cursor.lastrowid  
        conexion.cnx.commit()

    def load_all(self, conexion):
        query = """
        SELECT * FROM reserva
        """
        conexion.cursor.execute(query)
        resultado = conexion.cursor.fetchall()
        return resultado


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
        query_login = "INSERT INTO login (correo, contraseña) VALUES (%s, %s);"
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


class Sancion:
    def __init__(self, participante, fecha_inicio, fecha_fin):
        self.participante = participante
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.id_sancion = None  

    
    def __str__(self):
        return f"Sanción #{self.id_sancion or '—'} para {self.participante.nombre}: {self.fecha_inicio} → {self.fecha_fin}"

    
    def __repr__(self):
        return (f"Sancion(id_sancion={self.id_sancion!r}, participante={self.participante!r}, "
                f"fecha_inicio={self.fecha_inicio!r}, fecha_fin={self.fecha_fin!r})")

    def save(self, conexion):
        query = """
        INSERT INTO sancion_participante (ci, fecha_inicio, fecha_final)
        VALUES (%s, %s, %s);
        """
        conexion.cursor.execute(query, (self.participante.ci, self.fecha_inicio, self.fecha_fin))
        self.id_sancion = conexion.cursor.lastrowid  
        conexion.cnx.commit()

    def load_all(self, conexion):
        query = """
        SELECT * FROM sancion
        """
        conexion.cursor.execute(query)
        resultado = conexion.cursor.fetchall()
        return resultado


class ReservaParticipante:
    def __init__(self, reserva, participante, fecha_sol, asistencia):
        self.reserva = reserva
        self.participante = participante
        self.fecha_sol = fecha_sol
        self.asistencia = asistencia
        self.id_reserva_part = None  

    
    def __str__(self):
        estado = "Asistió" if self.asistencia else "No asistió"
        return f"ReservaParticipante #{self.id_reserva_part or '—'} — {self.participante.nombre} → {self.reserva.sala.nombre} ({estado})"

    
    def __repr__(self):
        return (f"ReservaParticipante(id_reserva_part={self.id_reserva_part!r}, reserva={self.reserva!r}, "
                f"fecha_sol={self.fecha_sol!r}, asistencia={self.asistencia!r}, participante={self.participante!r})")

    def save(self, conexion):
        if self.reserva.id_reserva is None:
            raise ValueError("Reserva.save() debe llamarse antes para obtener id_reserva")
        query = """
        INSERT INTO reserva_participante (ci, id_reserva, fecha_solicitud, asistencia)
        VALUES (%s, %s, %s, %s);
        """
        conexion.cursor.execute(query, (self.participante.ci, self.reserva.id_reserva, self.fecha_sol, self.asistencia))
        self.id_reserva_part = conexion.cursor.lastrowid  
        conexion.cnx.commit()

    def load_all(self, conexion):
        query = """
        SELECT * FROM reserva_participante
        """
        conexion.cursor.execute(query)
        resultado = conexion.cursor.fetchall()
        return resultado


class Facultad:
    def __init__(self, id_facultad, nombre):
        self.id = id_facultad
        self.nombre = nombre

    
    def __str__(self):
        return f"Facultad: {self.nombre} (ID: {self.id})"

    
    def __repr__(self):
        return f"Facultad(id={self.id!r}, nombre={self.nombre!r})"

    def save(self, conexion):
        query = """
        INSERT INTO facultad (id_facultad, nombre)
        VALUES (%s, %s);
        """
        conexion.cursor.execute(query, (self.id, self.nombre))
        conexion.cnx.commit()

    def load_all(self, conexion):
        query = """
        SELECT * FROM facultad
        """
        conexion.cursor.execute(query)
        resultado = conexion.cursor.fetchall()
        return resultado


class Programa:
    def __init__(self, facultad, tipo, nombre):
        self.facultad = facultad   # instancia Facultad
        self.tipo = tipo
        self.nombre = nombre

    
    def __str__(self):
        return f"Programa: {self.nombre} ({self.tipo}) — {self.facultad.nombre}"

    
    def __repr__(self):
        return (f"Programa(facultad={self.facultad!r}, tipo={self.tipo!r}, nombre={self.nombre!r})")

    def save(self, conexion):
        query = """
        INSERT INTO programa_academico (nombre_programa, id_facultad, tipo)
        VALUES (%s, %s, %s);
        """
        conexion.cursor.execute(query, (self.nombre, self.facultad.id, self.tipo))
        conexion.cnx.commit()

    def load_all(self, conexion):
        query = """
        SELECT * FROM programa_academico
        """
        conexion.cursor.execute(query)
        resultado = conexion.cursor.fetchall()
        return resultado


class ParticipantePrograma:
    def __init__(self, programa, participante, rol):
        self.programa = programa
        self.participante = participante
        self.rol = rol
        self.id_part_prog = None  

    
    def __str__(self):
        return f"{self.participante.nombre} ({self.rol}) en {self.programa.nombre}"


    def __repr__(self):
        return (f"ParticipantePrograma(id_part_prog={self.id_part_prog!r}, programa={self.programa!r}, "
                f"participante={self.participante!r}, rol={self.rol!r})")

    def save(self, conexion):
        query = """
        INSERT INTO participante_programa (rol, nombre_programa, ci)
        VALUES (%s, %s, %s);
        """
        conexion.cursor.execute(query, (self.rol, self.programa.nombre, self.participante.ci))
        self.id_part_prog = conexion.cursor.lastrowid  
        conexion.cnx.commit()

    def load_all(self, conexion):
        query = """
        SELECT * FROM participante_programa
        """
        conexion.cursor.execute(query)
        resultado = conexion.cursor.fetchall()
        return resultado
