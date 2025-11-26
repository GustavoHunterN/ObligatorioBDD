import datetime
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
        import control as cont
        # Check if edificio already exists
        if cont.edificio_exists(conexion, self.nombre):
            raise ValueError(f"El edificio '{self.nombre}' ya existe en la base de datos.")
        
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

    def __init__(self, nombre, capacidad, tipo, edificio):
        self.capacidad = capacidad
        self.edificio = edificio      # String o Edificio
        self.tipo_sala = tipo
        self.nombre = nombre

    
    def __str__(self):
        return f"Sala: {self.nombre} — Capacidad: {self.capacidad} — Tipo: {self.tipo_sala} — Edificio: {self.edificio}"

    
    def __repr__(self):
        return (f"Sala(nombre={self.nombre!r}, capacidad={self.capacidad!r}, "
                f"edificio={self.edificio!r}, tipo_sala={self.tipo_sala!r})")




    def save(self, conexion):
        import control as cont
        # Check if sala already exists
        if cont.sala_exists(conexion, self.nombre):
            raise ValueError(f"La sala '{self.nombre}' ya existe en la base de datos.")
        
        print("TIPO DE EDIFICIO:", type(self.edificio))
        print("VALOR DE EDIFICIO:", self.edificio)
        query = """
        INSERT INTO sala (nombre_sala, capacidad, tipo_sala, edificio)
        VALUES (%s, %s, %s, %s);
        """
        conexion.cursor.execute(query, (self.nombre, self.capacidad, self.tipo_sala, self.edificio))
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

    def __init__(self, sala, id_turno, edificio, estado, fecha):
        self.sala = sala
        self.id_turno = id_turno
        self.edificio = edificio
        self.estado = estado
        self.fecha = fecha
        self.id_reserva = None

    
    def __str__(self):
        return (f"Reserva #{self.id_reserva or '—'}: {self.sala.nombre} en {self.edificio.nombre} "
                f"({self.estado}) — {self.fecha}")

    
    def __repr__(self):
        return (f"Reserva(id_reserva={self.id_reserva!r}, sala={self.sala!r}, edificio={self.edificio!r}, "
                f"turno={self.id_turno!r}, estado={self.estado!r}, fecha={self.fecha!r})")

    def validar_sala(self):
        if not isinstance(self.sala, Sala):
            raise TypeError("La sala debe ser de tipo Sala")



    def save(self, conexion):
        import control as cont
        if self.id_turno is None:
            raise ValueError("Turnos.save() debe llamarse antes para obtener id_turno")
        
        # Check if there's already an active reserva for the same fecha, turno, sala, and edificio
        if cont.reserva_conflict_exists(conexion, self.fecha, self.id_turno, self.sala, self.edificio):
            raise ValueError(f"Ya existe una reserva activa para la sala '{self.sala}' en el edificio '{self.edificio}' "
                           f"para la fecha {self.fecha} y el turno {self.id_turno}.")
        
        query = """
        INSERT INTO reserva (fecha, estado, id_turno, nombre_edificio, sala)
        VALUES (%s, %s, %s, %s, %s);
        """

        conexion.cursor.execute(query, (self.fecha, self.estado, self.id_turno, self.edificio,self.sala))
        self.id_reserva = conexion.cursor.lastrowid
        conexion.cnx.commit()

    def load_all(self, conexion):
        query = """
        SELECT * FROM reserva
        """
        conexion.cursor.execute(query)
        resultado = conexion.cursor.fetchall()
        return resultado

class Sancion:
    def __init__(self, participante):
        self.participante = participante
        self.fecha_inicio = datetime.date.today()
        self.fecha_fin = self.fecha_inicio + datetime.timedelta(days=60)
        self.id_sancion = None  

    
    def __str__(self):
        return f"Sanción #{self.id_sancion or '—'} para {self.participante}: {self.fecha_inicio} → {self.fecha_fin}"

    
    def __repr__(self):
        return (f"Sancion(id_sancion={self.id_sancion!r}, participante={self.participante!r}, "
                f"fecha_inicio={self.fecha_inicio!r}, fecha_fin={self.fecha_fin!r})")

    def save(self, conexion):
        import control as cont
        # Check if participante already has an active sancion
        if cont.sancion_activa_exists(conexion, self.participante):
            raise ValueError(f"El participante con CI {self.participante} ya tiene una sanción activa.")
        
        query = """
        INSERT INTO sancion_participante (ci, fecha_inicio, fecha_final)
        VALUES (%s, %s, %s);
        """
        conexion.cursor.execute(query, (self.participante, self.fecha_inicio, self.fecha_fin))
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
    def __init__(self, id_reserva,participante,):
        self.id_reserva = int(id_reserva)
        self.participante = participante
        self.fecha_sol = datetime.date.today()
        self.asistencia = 0
        self.id_reserva_part = None

    
    def __str__(self):
        estado = "Asistió" if self.asistencia else "No asistió"
        return f"ReservaParticipante #{self.id_reserva_part or '—'} — {self.participante} → {self.id_reserva} ({estado})"

    
    def __repr__(self):
        return (f"ReservaParticipante(id_reserva_part={self.id_reserva_part!r}, reserva={self.id_reserva!r}, "
                f"fecha_sol={self.fecha_sol!r}, asistencia={self.asistencia!r}, participante={self.participante!r})")

    def save(self, conexion):
        import control as cont
        if self.id_reserva is None:
            raise ValueError("Reserva.save() debe llamarse antes para obtener id_reserva")
        
        # Check if participante is already associated with this reserva
        if cont.reserva_participante_exists(conexion, self.participante, self.id_reserva):
            raise ValueError(f"El participante con CI {self.participante} ya está asociado a la reserva #{self.id_reserva}.")
        
        query = """
        INSERT INTO reserva_participante (ci, id_reserva, fecha_solicitud, asistencia)
        VALUES (%s, %s, %s, %s);
        """
        conexion.cursor.execute(query, (self.participante, self.id_reserva, self.fecha_sol, self.asistencia))
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
    def __init__(self, nombre):
        self.nombre = nombre[0].upper() + nombre[1:].lower()

    
    def __str__(self):
        return f"Facultad: {self.nombre}"

    
    def __repr__(self):
        return f"Facultad(nombre={self.nombre!r})"

    def save(self, conexion):
        import control as cont
        # Check if facultad already exists
        if cont.facultad_exists(conexion, self.nombre):
            raise ValueError(f"La facultad '{self.nombre}' ya existe en la base de datos.")
        
        query = """
        INSERT INTO facultad (nombre)
        VALUES (%s);
        """
        conexion.cursor.execute(query, (self.nombre,))
        conexion.cnx.commit()

    def load_all(self, conexion):
        query = """
        SELECT * FROM facultad
        """
        conexion.cursor.execute(query)
        resultado = conexion.cursor.fetchall()
        return resultado


class Programa:
    def __init__(self,nombre,nombre_facultad,tipo):
        self.nombre_facultad = nombre_facultad
        self.tipo = tipo
        self.nombre = nombre

    
    def __str__(self):
        return f"Programa: {self.nombre} ({self.tipo})"

    
    def __repr__(self):
        return (f"Programa( tipo={self.tipo!r}, nombre={self.nombre!r})")

    def save(self, conexion):
        import control as cont
        # Check if programa already exists
        if cont.programa_exists(conexion, self.nombre):
            raise ValueError(f"El programa '{self.nombre}' ya existe en la base de datos.")
        
        query = """
        INSERT INTO programa_academico (nombre_programa, nombre_facultad, tipo)
        VALUES (%s, %s, %s);
        """
        conexion.cursor.execute(query, (self.nombre, self.nombre_facultad, self.tipo))
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
        import control as cont
        # Check if participante is already enrolled in this programa
        if cont.participante_programa_exists(conexion, self.participante, self.programa):
            raise ValueError(f"El participante con CI {self.participante} ya está inscrito en el programa '{self.programa}'.")
        
        query = """
        INSERT INTO participante_programa (rol, nombre_programa, ci)
        VALUES (%s, %s, %s);
        """
        conexion.cursor.execute(query, (self.rol, self.programa, self.participante))
        self.id_part_prog = conexion.cursor.lastrowid  
        conexion.cnx.commit()

    def load_all(self, conexion):
        query = """
        SELECT * FROM participante_programa
        """
        conexion.cursor.execute(query)
        resultado = conexion.cursor.fetchall()
        return resultado


class Participante:
    def __init__(self, ci, nombre, apellido, correo, contrasena, rol):
        self.ci = ci
        self.nombre = nombre
        self.apellido = apellido
        self.correo = correo
        self.contrasena = contrasena
        self.sanciones = []
        self.rol = rol

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.ci}) — {self.correo}"

    def __repr__(self):
        return (f"Participante(ci={self.ci!r}, nombre={self.nombre!r}, "
                f"apellido={self.apellido!r}, correo={self.correo!r})")

    def save(self, conexion):
        import control as cont
        # Check if participante already exists
        if cont.participante_exists(conexion, self.ci):
            raise ValueError(f"El participante con CI {self.ci} ya existe en la base de datos.")
        
        # Check if login (email) already exists
        if cont.login_exists(conexion, self.correo):
            raise ValueError(f"El correo '{self.correo}' ya está registrado en la base de datos.")
        
        query_login = "INSERT INTO login (correo, contrasena) VALUES (%s, %s);"
        query_part = """
        INSERT INTO participante (ci, nombre, apellido, correo, rol)
        VALUES (%s, %s, %s, %s, %s);
        """
        conexion.cursor.execute(query_login, (self.correo, self.contrasena))
        conexion.cursor.execute(query_part, (self.ci, self.nombre, self.apellido, self.correo, self.rol))
        conexion.cnx.commit()

    def load_all(self, conexion):
        query = """
        SELECT * FROM participante
        """
        conexion.cursor.execute(query)
        resultado = conexion.cursor.fetchall()
        return resultado


class Alumno(Participante):
    def __init__(self, ci, nombre, apellido, contrasena):
        self.ci  = f'{ci}A'
        self.nombre = f'{nombre[0].upper()+nombre[1:].lower()}'
        self.apellido = f'{apellido[0].upper()+apellido[1:].lower()}'
        self.correo = f"{self.nombre}.{self.apellido}@alumno.com"
        self.contrasena = contrasena
        self.rol = "Alumno"
        super().__init__(self.ci, self.nombre, self.apellido, self.correo, self.contrasena, self.rol)

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.ci}) — {self.correo}"

    def __repr__(self):
        return (f"Alumno(ci={self.ci!r}, nombre={self.nombre!r}, "
                f"apellido={self.apellido!r}, correo={self.correo!r})")


class Docente(Participante):
    def __init__(self, ci, nombre, apellido, contrasena):
        self.ci  = f'{ci}D'
        self.nombre = f'{nombre[0].upper()+nombre[1:].lower()}'
        self.apellido = f'{apellido[0].upper()+apellido[1:].lower()}'
        self.correo = f"{self.nombre}.{self.apellido}@docente.com"
        self.contrasena = contrasena
        self.rol = "Docente"
        super().__init__(self.ci, self.nombre, self.apellido, self.correo, self.contrasena, self.rol)

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.ci}) — {self.correo}"

    def __repr__(self):
        return (f"Docente(ci={self.ci!r}, nombre={self.nombre!r}, "
                f"apellido={self.apellido!r}, correo={self.correo!r})")
