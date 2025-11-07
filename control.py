import Clases as cl

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
                        {"Nombre": str}
          ,


          "Programa" :
                        {"Nombre": str,
                        "Tipo": ["Grado",
                                 "Posgrado"]
                         }
          ,


          "Participante" :
                        {"Nombre": str}
          ,


          "Participante_programa" :
                        {"Rol": ["Alumno",
                                 "Docente"]
                         }
          ,


          "Sala" :
                        {"capacidad": int,
                         "tipo": ["Grado",
                                  "Posgrado",
                                  "Libre"]
                     }
          ,



          "Edificio" : {"direccion": str,
                        "departamento": str},


          "Reserva" : {"Estado":["Activa",
                                 "Cancelada",
                                 "S/A",
                                 "Finalizada"]
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
                errores.append(f"{clase}.{atributo}: se esperaba {dominio.__name__}, se obtuvo {type(valor).__name__}")

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
    objeto = clase(*args)

    if check_dtypes(objeto, dtypes):
        return objeto
    return check_dtypes(objeto, dtypes)





