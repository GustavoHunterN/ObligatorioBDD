import Clases as cl
import datetime

#Diccionarios para controlar las keys

n_of_instances = {"Facultad" : 0,
                  "Programa" : 0,
                  "Participante_programa" : 0,
                  "Participante" : 0,
                  "Reserva" : 0,
                  "Reserva_programa" : 0,
                  "Sala" : 0,
                  "Edificio" : 0,
                  "Turnos" : 0
}

dtypes = {"Facultad" :
                        {
                         "facultad": object,
                         }
          ,


          "Programa" :
                        {"nombre": str,
                         "nombre_facultad": str,
                         "Tipo": ["Grado",
                                  "Posgrado"]
                         }
          ,


          "Participante" :
                        {"nombre": str,
                         "ci": str,
                         "apellido": str,
                         "correo": str,
                         "contrasena": str
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



          "Edificio" : {"direccion": str,
                        "departamento": str
                        },


          "Reserva" : {"id":str,
                       "sala": str,
                       "turno": str,
                        "estado":["Activa",
                                 "Cancelada",
                                 "S/A",
                                 "Finalizada"],
                       "fecha": str
                       },
          "ReservaParticipante" : {"id_reserva" : str,
                                   "participante": str,
                                    },
          "Sancion" : { "participante": object,
                        "fecha_inicio": str,
                        "fecha_fin": str
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
    clase = getattr(cl, nombre_clase, None)
    if clase is None:
        raise ValueError(f"Clase '{nombre_clase}' no encontrada en módulo cl.")

    # Si args tiene un solo elemento y ese elemento es una lista o tupla → desempacamos
    if len(args) == 1 and isinstance(args[0], (list, tuple)):
        args = args[0]
    print(args)
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





