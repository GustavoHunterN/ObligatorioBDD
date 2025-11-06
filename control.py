#Diccionarios para controlar la semántica de las keys

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