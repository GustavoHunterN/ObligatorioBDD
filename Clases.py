
class Edificio:
    def __init__(self,nombre, direccion, departamento):
        self.nombre = nombre
        self.direccion = direccion
        self.departamento = departamento

    def __str__(self):
        return f"Dirección: {self.direccion}, Departamento: {self.departamento}"

    def __repr__(self):
        return f"Edificio(direccion={self.direccion!r}, departamento={self.departamento!r})"


class Sala:
    def __init__(self, capacidad, edificio, tipo):

        self.capacidad = capacidad
        self.edificio = edificio
        self.tipo = tipo

    def __str__(self):
        return f"Sala: {self.nombre}, Capacidad: {self.capacidad}, Tipo: {self.tipo}, Edificio: {self.edificio.direccion}"

    def __repr__(self):
        return (f"Sala(nombre={self.nombre!r}, capacidad={self.capacidad!r}, "
                f"edificio={self.edificio!r}, tipo={self.tipo!r})")

    def validar_edificio(self):
        if not isinstance(self.edificio, Edificio):
            raise TypeError("El edificio debe ser de tipo Edificio")

    def set_nombre(self, num):
        self.nombre = str(self.edificio.nombre[0].upper() + "0" + num)


class Turnos:
    def __init__(self, horas, dia, sala):
        self.horas = horas
        self.dia = dia
        self.sala = sala

    def __str__(self):
        return f"Turno: {self.dia} a las {self.horas} en {self.sala.nombre}"

    def __repr__(self):
        return f"Turnos(horas={self.horas!r}, dia={self.dia!r}, sala={self.sala!r})"

    def validar_sala(self):
        if not isinstance(self.sala, Sala):
            raise TypeError("La sala debe ser de tipo Sala")


class Reserva:
    def __init__(self, id, sala, turno, estado, fecha):
        self.id = id
        self.sala = sala
        self.edificio = sala.edificio
        self.turno = turno
        self.estado = estado
        self.fecha = fecha

    def __str__(self):
        return (f"Reserva {self.id}: {self.sala.nombre} en {self.edificio.direccion} "
                f"({self.estado}) - {self.fecha}")

    def __repr__(self):
        return (f"Reserva(id={self.id!r}, sala={self.sala!r}, edificio={self.edificio!r}, "
                f"turno={self.turno!r}, estado={self.estado!r}, fecha={self.fecha!r})")

    def validar_sala(self):
        if not isinstance(self.sala, Sala):
            raise TypeError("La sala debe ser de tipo Sala")

    def validar_turno(self):
        if not isinstance(self.turno, Turnos):
            raise TypeError("El turno debe ser de tipo Turnos")


class Participante:
    def __init__(self, ci, nombre, apellido, correo, contrasena):
        self.ci = ci
        self.nombre = nombre
        self.apellido = apellido
        self.correo = correo
        self.contrasena = contrasena
        self.sanciones = []

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.ci}) - {self.correo}"

    def __repr__(self):
        return (f"Participante(ci={self.ci!r}, nombre={self.nombre!r}, "
                f"apellido={self.apellido!r}, correo={self.correo!r})")


class Sancion:
    def __init__(self, id, participante, fecha_inicio, fecha_fin):
        self.id = id
        self.participante = participante
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin

    def __str__(self):
        return f"Sanción {self.id} para {self.participante.nombre} ({self.fecha_inicio} - {self.fecha_fin})"

    def __repr__(self):
        return (f"Sancion(id={self.id!r}, participante={self.participante!r}, "
                f"fecha_inicio={self.fecha_inicio!r}, fecha_fin={self.fecha_fin!r})")


class ReservaParticipante:
    def __init__(self, reserva, fecha_sol, asistencia, participante):
        self.reserva = reserva
        self.fecha_sol = fecha_sol
        self.asistencia = asistencia
        self.participante = participante

    def __str__(self):
        return (f"ReservaParticipante: {self.participante.nombre} -> "
                f"{self.reserva.sala.nombre} ({'Asistió' if self.asistencia else 'No asistió'})")

    def __repr__(self):
        return (f"ReservaParticipante(reserva={self.reserva!r}, fecha_sol={self.fecha_sol!r}, "
                f"asistencia={self.asistencia!r}, participante={self.participante!r})")


class Facultad:
    def __init__(self, id, nombre):
        self.id = id
        self.nombre = nombre

    def __str__(self):
        return f"Facultad: {self.nombre} (ID: {self.id})"

    def __repr__(self):
        return f"Facultad(id={self.id!r}, nombre={self.nombre!r})"



class Programa:
    def __init__(self, facultad, tipo, nombre):
        self.facultad = facultad
        self.tipo = tipo
        self.nombre = nombre

    def __str__(self):
        return f"Programa: {self.nombre} ({self.tipo}) - {self.facultad.nombre}"

    def __repr__(self):
        return (f"Programa(facultad={self.facultad!r}, tipo={self.tipo!r}, nombre={self.nombre!r})")


class ParticipantePrograma:
    def __init__(self, programa, participante, id, rol):
        self.programa = programa
        self.participante = participante
        self.id = id
        self.rol = rol

    def __str__(self):
        return f"{self.participante.nombre} ({self.rol}) en {self.programa.nombre}"

    def __repr__(self):
        return (f"ParticipantePrograma(programa={self.programa!r}), participante={self.participante!r}, "
                f"id={self.id!r}, rol={self.rol!r})")




