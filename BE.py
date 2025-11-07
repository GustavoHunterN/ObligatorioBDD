# ---------- IMPORTS ----------
from Connector import Conexion
from Clases import (
    Edificio, Sala, Turnos, Reserva,
    Participante, Sancion, ReservaParticipante,
    Facultad, Programa, ParticipantePrograma
)
from datetime import datetime, date, time


# ---------- MAIN ----------
def main():
    print("🔗 Conectando a la base de datos...")
    con = Conexion()

    try:
        # 1️⃣ Crear un edificio
        edificio = Edificio("Mullin", "Rivera 1234", "Montevideo")
        id_edif = edificio.save(con)
        print(f"✅ Edificio guardado: {edificio}")

        # 2️⃣ Crear una sala asociada
        sala = Sala("M001", 40, edificio, "Teórica")
        sala.save(con)
        print(f"✅ Sala guardada: {sala}")

        # 3️⃣ Crear turno asociado
        turno = Turnos(time(9, 0), time(10, 0), date.today(), sala)
        turno.save(con)

        print(f"✅ Turno guardado: {turno}")

        # 4️⃣ Crear una reserva
        reserva = Reserva(sala, turno, "Activa", datetime.now())
        reserva.save(con)
        print(f"✅ Reserva creada: {reserva}")

        # 5️⃣ Crear participante
        participante = Participante("53241234", "Juan", "Pérez", "juan@example.com", "1234")
        participante.save(con)

        print(f"✅ Participante creado: {participante}")

        # 6️⃣ Asociar participante a reserva
        res_part = ReservaParticipante(reserva, participante, datetime.now(), True)
        res_part.save(con)
        print(f"✅ ReservaParticipante creada: {res_part}")

        # 7️⃣ Crear facultad y programa
        fac = Facultad("F01", "Ingeniería")
        fac.save(con)
        print(f"✅ Facultad creada: {fac}")

        prog = Programa(fac, "Grado", "Informática")
        prog.save(con)
        print(f"✅ Programa creado: {prog}")

        part_prog = ParticipantePrograma(prog, participante, "Alumno")
        part_prog.save(con)
        print(f"✅ ParticipantePrograma creado: {part_prog}")

        # 8️⃣ Consultas simples
        print("\n📋 Edificios existentes:")
        con.cursor.execute("SELECT * FROM edificio;")
        for fila in con.cursor.fetchall():
            print(fila)

    except Exception as e:
        print(f"❌ Error: {e}")

    finally:
        con.cerrar()
        print("🔒 Conexión cerrada.")


# ---------- ENTRY POINT ----------
if __name__ == "__main__":
    main()




