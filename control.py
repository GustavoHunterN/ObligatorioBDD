import Clases as cl


#Diccionarios para controlar las keys



dtypes = {"Facultad" :
                        {
                         "Nombre": str,
                         }
          ,


          "Programa" :
                        {"nombre": str,
                         "nombre_facultad": str,
                         "tipo": ["Grado",
                                  "Posgrado"]
                         }
          ,


          "Alumno" :
                        {"ci": str,
                         "nombre": str,
                         "apellido": str,
                         "contrasena": str,
                         }
          ,
          "Docente":
                {"ci": str,
                 "nombre": str,
                 "apellido": str,
                 "contrasena": str,
                 }
          ,


          "ParticipantePrograma" :
                        {"programa": str,
                         "participante": str,
                        "rol": ["Alumno",
                                 "Docente"],
                         }
          ,


          "Sala" :
                        {"nombre": str,
                        "capacidad": int,
                         "edificio" : str,
                         "tipo": ["Docente",
                                  "Posgrado",
                                  "Libre"]
                     }
          ,



          "Edificio" : {"nombre": str,
                        "direccion": str,
                        "departamento": str

                        },


          "Reserva" : {
                       "sala": str,
                       "id_turno": str,
                        "edificio": str,
                        "estado":["Activa",
                                 "Cancelada",
                                 "S/A",
                                 "Finalizada"],
                       "fecha": str
                       },

          "ReservaParticipante" : {"id_reserva" : str,
                                   "participante": str,
                                    },

          "Sancion" : { "participante": str,
                        },
          "Turnos" : { "hora_inicio": str,
                       "hora_final": str,
                       }
          }


            #obj = objeto a comparar
            # dtypes control.dtypes
def check_dtypes(obj, dtypes):
    clase = obj.__class__.__name__  # Nombre de la entidad (por ejemplo "Facultad")

    # Si la clase no tiene dominio definido, no se valida
    if clase not in dtypes:
        return True

    errores = []  # Acumulamos errores de validación
    esquema = dtypes[clase]  # Diccionario interno de atributos esperados

    for atributo, dominio in esquema.items():
        if not hasattr(obj, atributo):
            continue  # Si el objeto no tiene ese atributo, lo salteamos

        valor = getattr(obj, atributo)

        # Si el dominio es un tipo (ej: str, int)
        if isinstance(dominio, type):
            if not isinstance(valor, dominio):
                try:
                    # intentar conversión automática
                    valor_convertido = dominio(valor)
                    setattr(obj, atributo, valor_convertido)
                    print(obj, atributo, valor_convertido)
                except Exception:
                    errores.append(f"{clase}.{atributo}: se esperaba {dominio.__name__}, se obtuvo {type(valor).__name__}")
                    continue

        # Si el dominio es una lista de valores posibles
        elif isinstance(dominio, list):
            if valor not in dominio:
                errores.append(f"{clase}.{atributo}: '{valor}' no está dentro del dominio permitido {dominio}")

    # Resultado
    if errores:
        print("⚠️ Errores encontrados:")
        for e in errores:
            print("  -", e)
        return False

    print(f"✅ {clase}: todos los atributos válidos")
    return True

def create_objeto(nombre_clase, *args):
    print(f'control.py: creando objeto{nombre_clase}')
    clase = getattr(cl, nombre_clase, None)
    if clase is None:
        raise ValueError(f"Clase '{nombre_clase}' no encontrada en módulo cl.")

    # Si args tiene un solo elemento y ese elemento es una lista o tupla → desempacamos
    if len(args) == 1 and isinstance(args[0], (list, tuple)):
        args = args[0]
    print("Control.py: argumentos: ", args)
    objeto = clase(*args)
    validacion = check_dtypes(objeto, dtypes)

    if validacion:
        return objeto
    else:
        print(f"Error de tipo en {nombre_clase}: {validacion}")
        return None





def turnos_disponibles(fecha, conexion):
    """
    Retorna un diccionario donde:
    - si el turno tiene reserva activa ese día → "no_elegible"
    - si no tiene reserva → "elegible"
    """

    # 1. Obtener turnos fijos
    conexion.cursor.execute("SELECT id_turno FROM turnos")
    turnos = conexion.cursor.fetchall()

    # Diccionario base
    resultado = {t["id_turno"]: "elegible" for t in turnos}

    # 2. Obtener turnos reservados en esa fecha
    query = """
        SELECT id_turno 
        FROM reservas 
        WHERE fecha = %s AND estado = 'Activa'
    """
    conexion.cursor.execute(query, (fecha,))
    ocupados = conexion.cursor.fetchall()

    # 3. Marcar como NO elegibles
    for oc in ocupados:
        idt = oc["id_turno"]
        if idt in resultado:
            resultado[idt] = "no_elegible"

    return resultado


# control.py
#
def restriccion_reserva(conexion, ci, fecha, sala, rol, tipo_programa):
    """
    Restringe solo si la sala es de tipo 'Libre'.
    Docente en sala docente → sin restricciones.
    Posgrado → sin restricciones.
    """

    # Obtener tipo_sala
    conexion.cursor.execute("""
        SELECT tipo_sala
        FROM sala
        WHERE nombre_sala = %s;
    """, (sala,))
    tipo_sala = conexion.cursor.fetchone()["tipo_sala"]

    # --- Casos sin restricciones ---
    if tipo_sala != "Libre":
        return True, None

    if rol == "Docente" and tipo_sala == "Docente":
        return True, None

    if tipo_programa == "Posgrado":
        return True, None

    # --- Aplicar restricciones normales (alumno de grado en sala libre) ---
    # Límite diario
    conexion.cursor.execute("""
        SELECT COUNT(*) AS usadas
        FROM reserva r
        JOIN reserva_participante rp ON rp.id_reserva = r.id_reserva
        WHERE rp.ci = %s
          AND r.fecha = %s
          AND r.estado = 'Activa';
    """, (ci, fecha))
    dia = conexion.cursor.fetchone()["usadas"]

    if dia >= 2:
        return False, "No puedes reservar más de 2 horas por día."

    # Límite semanal
    conexion.cursor.execute("SELECT YEARWEEK(%s,1) AS sem", (fecha,))
    semana = conexion.cursor.fetchone()["sem"]

    conexion.cursor.execute("""
        SELECT COUNT(*) AS activas
        FROM reserva r
        JOIN reserva_participante rp ON rp.id_reserva = r.id_reserva
        WHERE rp.ci = %s
          AND r.estado = 'Activa'
          AND YEARWEEK(r.fecha,1) = %s;
    """, (ci, semana))
    sem = conexion.cursor.fetchone()["activas"]

    if sem >= 3:
        return False, "No puedes tener más de 3 reservas por semana."

    return True, None

def ordenar_args(nombre_clase, data):
    """
    Ordena los argumentos según el orden definido en dtypes[nombre_clase].
    - data: diccionario con los valores enviados desde el formulario
    - nombre_clase: string con el nombre de la clase que se quiere instanciar
    """

    if nombre_clase not in dtypes:
        raise ValueError(f"No existe definición de dtypes para {nombre_clase}")

    esquema = dtypes[nombre_clase] # Diccionario ordenado
    print(esquema)
    args = []
    errores = []

    for atributo in esquema.keys():
        if atributo not in data.keys():
            errores.append(f"Falta atributo obligatorio: {atributo}")
        else:
            print(atributo)
            args.append(data[atributo])  # esto mantiene el orden correcto

    if errores:
        print("Errores al crear args ordenados:")
        for e in errores:
            print(" -", e)
        return None

    # Debug: detectar atributos que no están en dtypes pero sí en data
    for key in data.keys():
        if key not in esquema:
            print(f'Control.py: ')
            print(f"⚠️ Advertencia: '{key}' no está definido en dtypes para '{nombre_clase}'")

    return args


def get_edificio_from_sala(conexion, sala):
    """
    Retorna el edificio al que pertenece una sala.
    Si la sala no existe, retorna None.
    """
    conexion.cursor.execute("""
        SELECT edificio
        FROM sala
        WHERE nombre_sala = %s
    """, (sala,))

    row = conexion.cursor.fetchone()
    return row["edificio"] if row else None

def Reserva_Lista_participantes(data, request):
    """
    Devuelve siempre una lista de CIs según el origen:
    - Docente: 'participantes_docente' (string con comas)
    - Alumno: 'participantes[]' (uno o varios valores en el form)
    """

    # Caso docente: lista en formato "ci1,ci2,ci3"
    if "participantes_docente" in data:
        return data["participantes_docente"].split(",")

    # Caso alumno
    if "participantes[]" in data:
        raw_list = request.form.getlist("participantes[]")
        if isinstance(raw_list, list):
            return raw_list
        else:
            return [raw_list]

    # Si no hay participantes, retornar lista vacía
    return []

def obtener_salas_filtradas(salas_all, rol, tipo_programa):
    """
    Retorna una lista de salas que el usuario puede reservar,
    según su rol (Alumno/Docente) y el tipo de programa (Grado/Posgrado).
    """

    salas_filtradas = []

    for s in salas_all:
        # DOCENTE: Libre y Docente
        if rol == "Docente":
            if s["tipo_sala"] in ("Libre", "Docente"):
                salas_filtradas.append(s)

        # ALUMNO:
        elif rol == "Alumno":
            # Grado: Solo Libre
            if tipo_programa == "Grado" and s["tipo_sala"] == "Libre":
                salas_filtradas.append(s)

            # Posgrado: Libre + Posgrado
            elif tipo_programa == "Posgrado" and s["tipo_sala"] in ("Libre", "Posgrado"):
                salas_filtradas.append(s)

    return salas_filtradas


def obtener_turnos(conexion):
    """Devuelve todos los turnos."""
    conexion.cursor.execute("SELECT * FROM turnos;")
    return conexion.cursor.fetchall()

def obtener_edificios(conexion):
    conexion.cursor.execute("SELECT * FROM edificio;")
    return conexion.cursor.fetchall()

def obtener_reserva_por_id(conexion, id_reserva):
    """
    Trae una reserva por ID o retorna None si no existe.
    """
    conexion.cursor.execute("""
        SELECT *
        FROM reserva
        WHERE id_reserva = %s;
    """, (id_reserva,))
    return conexion.cursor.fetchone()


def obtener_participantes_reserva(conexion, id_reserva):
    """Devuelve lista de CIs que están en esta reserva."""
    conexion.cursor.execute("""
        SELECT ci
        FROM reserva_participante
        WHERE id_reserva = %s;
    """, (id_reserva,))
    rows = conexion.cursor.fetchall()
    return [r["ci"] for r in rows]

def obtener_participantes_programa(conexion, nombre_programa):
    """
    Devuelve lista de participantes (con ci, nombre, apellido)
    que pertenecen a un programa.
    """
    conexion.cursor.execute("""
        SELECT p.ci, p.nombre, p.apellido
        FROM participante_programa pp
        JOIN participante p ON p.ci = pp.ci
        WHERE pp.nombre_programa = %s;
    """, (nombre_programa,))
    return conexion.cursor.fetchall()


def editar_lista_participantes(conexion, programa, ci_usuario):
    """
    Lista de participantes del programa para edición de reserva,
    EXCLUYENDO al usuario actual.
    """
    participantes = obtener_participantes_programa(conexion, programa)
    return [p for p in participantes if p["ci"] != ci_usuario]



def restriccion_reserva_editar(conexion, ci, fecha_nueva, id_reserva_actual, sala, rol, tipo_programa):

    # Obtener tipo de sala
    conexion.cursor.execute("""
        SELECT tipo_sala
        FROM sala
        WHERE nombre_sala = %s;
    """, (sala,))
    tipo_sala = conexion.cursor.fetchone()["tipo_sala"]

    # --- EXCEPCIONES ---
    if tipo_sala != "Libre":
        return True, None

    if rol == "Docente" and tipo_sala == "Docente":
        return True, None

    if tipo_programa == "Posgrado":
        return True, None

    # --- RESTRICCIONES NORMALES ---
    conexion.cursor.execute("""
        SELECT COUNT(*) AS usadas
        FROM reserva r
        JOIN reserva_participante rp ON rp.id_reserva = r.id_reserva
        WHERE rp.ci = %s
          AND r.fecha = %s
          AND r.estado = 'Activa'
          AND r.id_reserva <> %s;
    """, (ci, fecha_nueva, id_reserva_actual))
    dia = conexion.cursor.fetchone()["usadas"]

    if dia >= 2:
        return False, "No puedes superar 2 horas por día."

    conexion.cursor.execute("SELECT YEARWEEK(%s,1) AS sem", (fecha_nueva,))
    semana = conexion.cursor.fetchone()["sem"]

    conexion.cursor.execute("""
        SELECT COUNT(*) AS usadas
        FROM reserva r
        JOIN reserva_participante rp ON rp.id_reserva = r.id_reserva
        WHERE rp.ci = %s
          AND r.estado = 'Activa'
          AND YEARWEEK(r.fecha, 1) = %s
          AND r.id_reserva <> %s;
    """, (ci, semana, id_reserva_actual))
    sem = conexion.cursor.fetchone()["usadas"]

    if sem >= 3:
        return False, "No puedes superar 3 reservas activas por semana."

    return True, None


def turno_ocupado_en_edicion(conexion, sala, edificio, fecha, id_turno, id_reserva_actual):
    """
    Devuelve True si el turno está ocupado por otra reserva (distinta a la actual).
    Devuelve False si está libre.
    """

    conexion.cursor.execute("""
        SELECT 1
        FROM reserva
        WHERE sala = %s
          AND nombre_edificio = %s
          AND fecha = %s
          AND id_turno = %s
          AND estado = 'Activa'
          AND id_reserva <> %s;
    """, (sala, edificio, fecha, id_turno, id_reserva_actual))

    return conexion.cursor.fetchone() is not None

def obtener_participantes_reserva_detallado(conexion, id_reserva):
    conexion.cursor.execute("""
        SELECT 
            rp.ci,
            rp.asistencia,
            p.nombre,
            p.apellido
        FROM reserva_participante rp
        JOIN participante p ON p.ci = rp.ci
        WHERE rp.id_reserva = %s;
    """, (id_reserva,))
    return conexion.cursor.fetchall()


def ninguno_asistio(conexion, id_reserva):
    """
    Devuelve True si ningún participante asistió a la reserva.
    Devuelve False si al menos uno asistió.
    """
    conexion.cursor.execute("""
        SELECT COUNT(*) AS presentes
        FROM reserva_participante
        WHERE id_reserva = %s AND asistencia = 1;
    """, (id_reserva,))
    presentes = conexion.cursor.fetchone()["presentes"]
    return presentes == 0


def participantes_de_reserva(conexion, id_reserva):
    """
    Devuelve lista de CIs de todos los participantes de una reserva.
    """
    conexion.cursor.execute("""
        SELECT ci
        FROM reserva_participante
        WHERE id_reserva = %s;
    """, (id_reserva,))
    return [row["ci"] for row in conexion.cursor.fetchall()]


def tiene_sancion_activa(conexion, ci):
    """
    Devuelve True si el participante tiene una sanción vigente.
    """
    conexion.cursor.execute("""
        SELECT 1
        FROM sancion_participante
        WHERE ci = %s
          AND fecha_final >= CURDATE();
    """, (ci,))

    return conexion.cursor.fetchone() is not None


# -------------------- SANCIONES HELPERS --------------------

def obtener_sanciones(conexion):
    """
    Devuelve todas las sanciones con datos del participante.
    """
    conexion.cursor.execute("""
        SELECT sp.id_sancion,
               sp.ci,
               p.nombre,
               p.apellido,
               sp.fecha_inicio,
               sp.fecha_final
        FROM sancion_participante sp
        JOIN participante p ON p.ci = sp.ci
        ORDER BY sp.fecha_inicio DESC, sp.id_sancion DESC;
    """)
    return conexion.cursor.fetchall()


def obtener_sancion_por_id(conexion, id_sancion):
    conexion.cursor.execute("""
        SELECT sp.id_sancion,
               sp.ci,
               p.nombre,
               p.apellido,
               sp.fecha_inicio,
               sp.fecha_final
        FROM sancion_participante sp
        JOIN participante p ON p.ci = sp.ci
        WHERE sp.id_sancion = %s;
    """, (id_sancion,))
    return conexion.cursor.fetchone()


def actualizar_sancion(conexion, id_sancion, fecha_final):
    conexion.cursor.execute("""
        UPDATE sancion_participante
        SET fecha_final = %s
        WHERE id_sancion = %s;
    """, (fecha_final, id_sancion))


def eliminar_sancion(conexion, id_sancion):
    conexion.cursor.execute("""
        DELETE FROM sancion_participante
        WHERE id_sancion = %s;
    """, (id_sancion,))


# ==================== EXISTENCE CHECK FUNCTIONS ====================
# Centralized functions to check if records exist before INSERT operations

def edificio_exists(conexion, nombre_edificio):
    """Check if an edificio with the given name already exists."""
    conexion.cursor.execute("""
        SELECT 1 FROM edificio WHERE nombre_edificio = %s LIMIT 1
    """, (nombre_edificio,))
    return conexion.cursor.fetchone() is not None


def sala_exists(conexion, nombre_sala):
    """Check if a sala with the given name already exists."""
    conexion.cursor.execute("""
        SELECT 1 FROM sala WHERE nombre_sala = %s LIMIT 1
    """, (nombre_sala,))
    return conexion.cursor.fetchone() is not None


def participante_exists(conexion, ci):
    """Check if a participante with the given CI already exists."""
    conexion.cursor.execute("""
        SELECT 1 FROM participante WHERE ci = %s LIMIT 1
    """, (ci,))
    return conexion.cursor.fetchone() is not None


def login_exists(conexion, correo):
    """Check if a login with the given email already exists."""
    conexion.cursor.execute("""
        SELECT 1 FROM login WHERE correo = %s LIMIT 1
    """, (correo,))
    return conexion.cursor.fetchone() is not None


def facultad_exists(conexion, nombre):
    """Check if a facultad with the given name already exists."""
    conexion.cursor.execute("""
        SELECT 1 FROM facultad WHERE nombre = %s LIMIT 1
    """, (nombre,))
    return conexion.cursor.fetchone() is not None


def programa_exists(conexion, nombre_programa):
    """Check if a programa with the given name already exists."""
    conexion.cursor.execute("""
        SELECT 1 FROM programa_academico WHERE nombre_programa = %s LIMIT 1
    """, (nombre_programa,))
    return conexion.cursor.fetchone() is not None


def participante_programa_exists(conexion, ci, nombre_programa):
    """Check if a participante is already enrolled in a programa."""
    conexion.cursor.execute("""
        SELECT 1 FROM participante_programa 
        WHERE ci = %s AND nombre_programa = %s LIMIT 1
    """, (ci, nombre_programa))
    return conexion.cursor.fetchone() is not None


def reserva_participante_exists(conexion, ci, id_reserva):
    """Check if a participante is already associated with a reserva."""
    conexion.cursor.execute("""
        SELECT 1 FROM reserva_participante 
        WHERE ci = %s AND id_reserva = %s LIMIT 1
    """, (ci, id_reserva))
    return conexion.cursor.fetchone() is not None


def reserva_conflict_exists(conexion, fecha, id_turno, sala, nombre_edificio):
    """Check if an active reserva already exists for the same fecha, turno, sala, and edificio."""
    conexion.cursor.execute("""
        SELECT 1 FROM reserva 
        WHERE fecha = %s 
          AND id_turno = %s 
          AND sala = %s 
          AND nombre_edificio = %s 
          AND estado = 'Activa' 
        LIMIT 1
    """, (fecha, id_turno, sala, nombre_edificio))
    return conexion.cursor.fetchone() is not None


def sancion_activa_exists(conexion, ci):
    """Check if the participante already has an active sancion."""
    conexion.cursor.execute("""
        SELECT 1 FROM sancion_participante 
        WHERE ci = %s 
          AND (fecha_final IS NULL OR fecha_final >= CURDATE())
        LIMIT 1
    """, (ci,))
    return conexion.cursor.fetchone() is not None


# ==================== OWNERSHIP VERIFICATION FUNCTIONS ====================
# Functions to verify user ownership of resources using JOINs with parameterized queries

def usuario_es_participante_reserva(conexion, ci, id_reserva):
    """
    Verifica que el usuario (ci) es participante de la reserva (id_reserva).
    Usa JOIN para verificar ownership y prevenir SQL injection.
    Retorna True si el usuario es participante, False en caso contrario.
    """
    conexion.cursor.execute("""
        SELECT 1
        FROM reserva_participante rp
        JOIN reserva r ON r.id_reserva = rp.id_reserva
        WHERE rp.ci = %s AND rp.id_reserva = %s
        LIMIT 1
    """, (ci, id_reserva))
    return conexion.cursor.fetchone() is not None


def usuario_esta_en_programa(conexion, ci, nombre_programa):
    """
    Verifica que el usuario (ci) está inscrito en el programa (nombre_programa).
    Usa JOIN para verificar ownership y prevenir SQL injection.
    Retorna True si el usuario está en el programa, False en caso contrario.
    """
    conexion.cursor.execute("""
        SELECT 1
        FROM participante_programa pp
        JOIN programa_academico pa ON pa.nombre_programa = pp.nombre_programa
        WHERE pp.ci = %s AND pp.nombre_programa = %s
        LIMIT 1
    """, (ci, nombre_programa))
    return conexion.cursor.fetchone() is not None