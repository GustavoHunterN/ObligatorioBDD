from mysql.connector.errors import IntegrityError
import datetime
from flask import (
    Flask, render_template, request, jsonify,
    flash, redirect, url_for, session
)
import control as cont
from Connector import Conexion

app = Flask(__name__)
app.secret_key = "supersecret123"   # Cámbiala si es producción



@app.route('/')
def index():
    session.pop('_flashes', None)
    return render_template('base.html')


def require_role(role: str):
    """Middleware simple para validar acceso por rol."""
    if session.get("rol") != role:
        flash("Acceso no autorizado.", "error")
        return redirect(url_for(f'login_{role.lower()}_form'))


@app.route('/login/alumno', methods=['GET'])
def login_alumno_form():
    session.pop('_flashes', None)
    return render_template('login_alumno.html')

@app.route('/login/docente', methods=['GET'])
def login_docente_form():
    session.pop('_flashes', None)
    return render_template('login_docente.html')


@app.route('/login/alumno', methods=['POST'])
def login_alumno():
    correo = request.form.get('correo')
    contrasena = request.form.get('contrasena')
    print("== LOGIN ALUMNO ==")
    print("correo:", correo)
    print("pass:", contrasena)

    if not (correo and contrasena):
        flash("Debes ingresar correo y contraseña.", "login_error")
        return redirect(url_for('login_alumno_form'))

    conexion = Conexion()

    # Login sin necesidad de tener programa
    conexion.cursor.execute("""
        SELECT 
            p.ci,
            p.nombre,
            p.apellido,
            p.correo
        FROM participante p
        JOIN login l ON l.correo = p.correo
        WHERE l.correo = %s
          AND l.contrasena = %s
          AND RIGHT(p.ci, 1) = 'A'
        LIMIT 1;
    """, (correo, contrasena))

    user = conexion.cursor.fetchone()
    print("SQL RESULT:", user)

    if not user:
        conexion.cerrar()
        flash("Credenciales inválidas para alumno.", "login_error")
        return redirect(url_for('login_alumno_form'))

    # Cargar datos base en session
    session["ci"] = user["ci"]
    session["nombre"] = user["nombre"]
    session["apellido"] = user["apellido"]
    session["correo"] = user["correo"]
    session["rol"] = "Alumno"

    # Verificar si está inscripto en algún programa
    conexion.cursor.execute("""
        SELECT pp.nombre_programa, pr.tipo
        FROM participante_programa pp
        JOIN programa_academico pr ON pr.nombre_programa = pp.nombre_programa
        WHERE pp.ci = %s
    """, (session["ci"],))

    programas = conexion.cursor.fetchall()
    conexion.cerrar()

    if not programas:
        flash("Debes inscribirte en un programa antes de continuar.", "error")
        return redirect(url_for("form_participanteprograma"))

    # Tomamos el primer programa (o el que quieras)
    programa = programas[0]
    session["programa"] = programa["nombre_programa"]
    session["tipo_programa"] = programa["tipo"]

    flash(f"Bienvenido, {user['nombre']}", "ok")
    return redirect(url_for('dashboard_alumno'))


@app.route('/alumno/home')
def dashboard_alumno():
    unauthorized = require_role("Alumno")

    if unauthorized:
        return unauthorized
    return f"""<h1>Alumno: {session['nombre']} {session['apellido']}</h1>
            <h2> Sesión iniciada con éxito</h2>
            {dict(session)}"""




@app.route('/login/docente', methods=['POST'])
def login_docente():
    correo = request.form.get('correo')
    contrasena = request.form.get('contrasena')
    print("== LOGIN DOCENTE ==")
    print("correo:", correo)
    print("pass:", contrasena)


    if not (correo and contrasena):
        flash("Debes ingresar correo y contraseña.", "login_error")
        return redirect(url_for('login_docente_form'))

    conexion = Conexion()

    # Login sin depender de participante_programa
    conexion.cursor.execute("""
        SELECT 
            p.ci,
            p.nombre,
            p.apellido,
            p.correo
        FROM participante p
        JOIN login l ON l.correo = p.correo
        WHERE l.correo = %s
          AND l.contrasena = %s
          AND RIGHT(p.ci, 1) = 'D'
        LIMIT 1;
    """, (correo, contrasena))

    user = conexion.cursor.fetchone()
    print("SQL RESULT:", user)

    if not user:
        conexion.cerrar()
        flash("Credenciales inválidas para docente.", "login_error")
        return redirect(url_for('login_docente_form'))

    # Cargar sesión
    session["ci"] = user["ci"]
    session["nombre"] = user["nombre"]
    session["apellido"] = user["apellido"]
    session["correo"] = user["correo"]
    session["rol"] = "Docente"

    # Verificar programas
    conexion.cursor.execute("""
        SELECT pp.nombre_programa, pr.tipo
        FROM participante_programa pp
        JOIN programa_academico pr ON pr.nombre_programa = pp.nombre_programa
        WHERE pp.ci = %s
    """, (session["ci"],))

    programas = conexion.cursor.fetchall()
    conexion.cerrar()

    if not programas:
        flash("Debes estar asignado a al menos un programa.", "error")
        return redirect(url_for("form_participanteprograma"))

    programa = programas[0]
    session["programa"] = programa["nombre_programa"]
    session["tipo_programa"] = programa["tipo"]

    flash(f"Bienvenido, {user['nombre']}", "ok")
    return redirect(url_for('dashboard_docente'))


@app.route('/docente/home')
def dashboard_docente():
    unauthorized = require_role("Docente")
    if unauthorized:
        return unauthorized
    return f"""<h1>Docente: {session['nombre']} {session['apellido']}</h1>
            <h2> Sesión iniciada con éxito</h2>
            {dict(session)}"""


@app.route('/alumnos/nuevo', methods=['GET'])
def form_alumno():
    return render_template('alumno_form.html')


@app.route('/docentes/nuevo', methods=['GET'])
def form_docente():
    return render_template('docente_form.html')


@app.route('/FormularioEdificio', methods=['GET'])
def form_edificio():
    return render_template('edificio_form.html')

@app.route('/FormularioSala', methods=['GET'])
def form_sala():
    conexion = Conexion()
    conexion.cursor.execute("SELECT nombre_edificio FROM edificio")
    edificios = conexion.cursor.fetchall()
    conexion.cerrar()

    return render_template("sala_form.html", edificios=edificios)

@app.route('/ObjectCreator', methods=['POST'])
def object_creator():
    data = request.form.to_dict()  # Convertimos a dict editable
    print("DATA COMPLETO:", data)
    nombre_clase = data.get('class_name')
    tipo_clase = data.get('type')

    if nombre_clase == "Sala" and "cantidad" in data:
        cantidad = int(data["cantidad"])
        capacidad = int(data["capacidad"])
        tipo = data["tipo"]
        edificio = data["edificio"]
        data.pop("cantidad")
        conexion = Conexion()
        for i in range(1, cantidad + 1):
            nombre_sala = f"{edificio[0].upper()}{i:03d}"
            obj = cont.create_objeto("Sala", [nombre_sala, capacidad, tipo, edificio])
            obj.save(conexion)
        conexion.cerrar()
        flash(f"{cantidad} salas generadas correctamente", "ok")
        return redirect(url_for('form_sala'))


    # Agregar sufijo según tipo de participante
    if nombre_clase == 'Participante':
        sufijo = 'A' if tipo_clase == 'alumno' else 'D'
        data['ci'] = data['ci'] + sufijo
    # ============================
    # ARMAR ARGUMENTOS RESERVA CORRECTOS
    # ============================
    # =======================
    # RESERVA → MULTIPLES PARTICIPANTES
    # =======================
    # =======================
    # RESERVA → MULTIPLES PARTICIPANTES
    # =======================
    if nombre_clase == 'Reserva':

        if "edificio" not in data:
            conexion_temp = Conexion()
            conexion_temp.cursor.execute("""
                SELECT edificio 
                FROM sala 
                WHERE nombre_sala = %s
            """, (data["sala"],))
            row = conexion_temp.cursor.fetchone()
            conexion_temp.cerrar()
            if row:
                data["edificio"] = row["edificio"]
                print(data["edificio"])
            else:
                raise ValueError("No se pudo obtener el edificio para esa sala.")

        # Ahora sí, construir ARGS en el ORDEN CORRECTO
        args_reserva = [
            data["sala"],  # sala
            data["id_turno"],  # id_turno
            data["edificio"],  # edificio (ya asegurado)
            data["estado"],  # estado
            data["fecha"]  # fecha
        ]

        print("ARGS RESERVA:", args_reserva)
        objeto = cont.create_objeto("Reserva", args_reserva)

    if not objeto:
        return jsonify({"error": "Datos inválidos"}), 400

    conexion = Conexion()
    if not tipo_clase:
        object_temp = f'form_{nombre_clase.lower()}'
    else:
        object_temp = f'form_{tipo_clase.lower()}'
    ci_base = session['ci']
    if hasattr(objeto, "save"):
        try:
            # 1) Verificar límite diario (máx 2 horas → 2 turnos)
            conexion.cursor.execute("""
                 SELECT COUNT(*) AS usadas
                 FROM reserva r
                 JOIN reserva_participante rp ON rp.id_reserva = r.id_reserva
                 WHERE rp.ci = %s
                   AND r.fecha = %s
                   AND r.estado = 'Activa';
             """, (ci_base, data["fecha"]))

            limite_dia = conexion.cursor.fetchone()["usadas"]
            if limite_dia >= 2:
                conexion.cerrar()
                flash("No puedes reservar más de 2 horas por día.", "error")
                return redirect(url_for("form_reserva"))
            # Calcular rango semanal
            conexion.cursor.execute("""
                 SELECT YEARWEEK(%s, 1) AS sem
             """, (data["fecha"],))
            week_code = conexion.cursor.fetchone()["sem"]

            conexion.cursor.execute("""
                 SELECT COUNT(*) AS activas
                 FROM reserva r
                 JOIN reserva_participante rp ON rp.id_reserva = r.id_reserva
                 WHERE rp.ci = %s
                   AND r.estado = 'Activa'
                   AND YEARWEEK(r.fecha, 1) = %s;
             """, (ci_base, week_code))

            limite_semana = conexion.cursor.fetchone()["activas"]

            if limite_semana >= 3:
                conexion.cerrar()
                flash("No puedes tener más de 3 reservas activas en una misma semana.", "error")
                return redirect(url_for("form_reserva"))
            objeto.save(conexion)
            # ----------------------------------------------------------
            # CREAR RESERVA_PARTICIPANTE PARA TODOS LOS INVITADOS
            # ----------------------------------------------------------
            if nombre_clase == "Reserva":
                lista_cis = []

                # Caso docente → viene en participantes_docente como "ci1,ci2,ci3"
                if "participantes_docente" in data:
                    lista_cis = data["participantes_docente"].split(",")

                # Caso alumno → viene como participantes[] (un String o varios)
                elif "participantes[]" in data:
                    raw = request.form.getlist("participantes[]")
                    # raw puede ser una lista o un solo string → normalizamos
                    if isinstance(raw, list):
                        lista_cis = raw
                    else:
                        lista_cis = [raw]

                # Ahora sí: crear una fila por cada participante
                for ci_part in lista_cis:
                    conexion.cursor.execute("""
                        INSERT INTO reserva_participante (ci, id_reserva, fecha_solicitud, asistencia)
                        VALUES (%s, %s, NOW(), NULL)
                    """, (ci_part, objeto.id_reserva))

                conexion.cnx.commit()

        except Exception as e:
            session.pop('flashes', None)
            flash(f"Error inesperado: {str(e)}", "error")
            return render_template('base.html')


        except IntegrityError:
            session.pop('flashes', None)
            flash("El objeto ya existe o viola una restricción única.", "error")
            if not tipo_clase:
                return redirect(url_for(object_temp))
            else:
                return redirect(url_for(object_temp))
        except Exception as e:
            session.pop('flashes', None)
            flash(f"Error inesperado: {str(e)}", "error")
            return render_template('base.html')
    else:
        conexion.cerrar()
        return jsonify({"error": f"La clase {nombre_clase} no tiene método save()"}), 400

    conexion.cerrar()
    session.pop('_flashes', None)
    print(f"{nombre_clase} creado correctamente.", "ok")
    flash(f"{nombre_clase} creado correctamente.", "ok")
    return redirect(url_for(object_temp))



@app.route('/FormularioFacultad', methods=['GET'])
def form_facultad():
    return render_template('facultad_form.html')



@app.route('/FormularioPrograma')
def form_programa():
    conexion = Conexion()
    conexion.cursor.execute("SELECT nombre FROM facultad;")
    facultades = conexion.cursor.fetchall()
    conexion.cerrar()

    return render_template("programa_form.html", facultades=facultades)



@app.route('/edificios/listar', methods=['GET'])
def listar_edificios():
    conexion = Conexion()
    conexion.cursor.execute("SELECT nombre_edificio, direccion, departamento FROM edificio;")
    edificios = conexion.cursor.fetchall()
    conexion.cerrar()
    return render_template('lista_edificios.html', edificios=edificios)


@app.route('/reserva/crear', methods=['GET'])
def form_reserva():
    ci_sesion = session.get("ci")
    fecha = request.args.get("fecha")
    if not fecha:
        fecha = datetime.date.today()
    filtro_edificio = request.args.get("edificio")
    filtro_turno = request.args.get("id_turno")

    conexion = Conexion()

    # Edificios
    conexion.cursor.execute("SELECT nombre_edificio FROM edificio;")
    edificios = conexion.cursor.fetchall()

    # Turnos
    conexion.cursor.execute("SELECT * FROM turnos;")
    todos_los_turnos = conexion.cursor.fetchall()
    turnos = todos_los_turnos
    # Aplicar filtro de turno
    if filtro_turno:
        try:
            filtro_turno = int(filtro_turno)
            turnos = [t for t in todos_los_turnos if t["id_turno"] == filtro_turno]
        except ValueError:
            pass

    # Salas con filtro
    if filtro_edificio:
        conexion.cursor.execute("SELECT * FROM sala WHERE edificio=%s;", (filtro_edificio,))
    else:
        conexion.cursor.execute("SELECT * FROM sala;")
    salas = conexion.cursor.fetchall()

    # === FILTRAR SALAS SEGÚN ROL Y PROGRAMA SELECCIONADO ===

    rol = session.get("rol")  # Alumno / Docente
    programa_reserva = session.get("programa_reserva") or session.get("programa")

    # Obtener tipo del programa desde DB
    conexion.cursor.execute("""
        SELECT tipo FROM programa_academico
        WHERE nombre_programa = %s
    """, (programa_reserva,))
    row = conexion.cursor.fetchone()

    tipo_prog_reserva = row["tipo"] if row else None

    salas_filtradas = []

    for s in salas:
        # DOCENTE: Libre y Docente
        if rol == "Docente":
            if s["tipo_sala"] in ("Libre", "Docente"):
                salas_filtradas.append(s)

        # ALUMNO: según el programa desde el que entra
        elif rol == "Alumno":
            # Grado → solo Libre
            if tipo_prog_reserva == "Grado" and s["tipo_sala"] == "Libre":
                salas_filtradas.append(s)

            # Posgrado → Libre y Posgrado
            elif tipo_prog_reserva == "Posgrado" and s["tipo_sala"] in ("Libre", "Posgrado"):
                salas_filtradas.append(s)

    salas = salas_filtradas

    # ========================================================

    # Reservados por fecha
    reservados = set()
    if fecha:
        conexion.cursor.execute("""
            SELECT id_turno, sala, nombre_edificio
            FROM reserva
            WHERE fecha = %s
            AND estado = 'Activa';
        """, (fecha,))
        reservados = set(
            (r["id_turno"], r["sala"], r["nombre_edificio"])
            for r in conexion.cursor.fetchall()
        )

    conexion.cerrar()
    fecha_hoy = datetime.date.today().isoformat()
    return render_template(
        "Reserva_form.html",
        salas=salas,
        turnos=turnos,
        todos_los_turnos=todos_los_turnos,
        edificios=edificios,
        reservados=reservados,
        fecha=fecha,
        filtro_edificio=filtro_edificio,
        filtro_turno=filtro_turno,
        ci_sesion = ci_sesion,
        fecha_hoy = fecha_hoy
    )

@app.route('/reserva/participantes')
def seleccionar_participantes():
    ci = session.get("ci")
    rol = session.get("rol")
    programa = session.get("programa_reserva")

    if not ci or not programa:
        flash("Debe seleccionar un programa antes de reservar.", "error")
        return redirect(url_for('mis_programas'))

    sala = request.args.get("sala")
    id_turno = request.args.get("id_turno")
    fecha = request.args.get("fecha")

    conexion = Conexion()

    # Obtener datos de la sala
    conexion.cursor.execute("""
        SELECT nombre_sala, capacidad, tipo_sala, edificio
        FROM sala
        WHERE nombre_sala = %s;
    """, (sala,))
    datos_sala = conexion.cursor.fetchone()

    if not datos_sala:
        conexion.cerrar()
        flash("Sala no encontrada.", "error")
        return redirect(url_for("form_reserva"))

    capacidad = datos_sala["capacidad"]

    # Obtener participantes del programa
    conexion.cursor.execute("""
        SELECT p.ci, p.nombre, p.apellido
        FROM participante_programa pp
        JOIN participante p ON p.ci = pp.ci
        WHERE pp.nombre_programa = %s;
    """, (programa,))
    participantes = conexion.cursor.fetchall()

    conexion.cerrar()

    # DOCENTE: reservar para todos
    if rol == "Docente":
        if len(participantes) > capacidad:
            flash("La sala no tiene capacidad suficiente para todos los participantes del programa.", "error")
            return redirect(url_for('form_reserva'))

        return render_template(
            "reserva_confirmar_docente.html",
            participantes=participantes,
            sala=sala,
            fecha=fecha,
            id_turno=id_turno,
            capacidad=capacidad,
            programa=programa
        )

    # ALUMNO: elegir participantes
    return render_template(
        "reserva_elegir_participantes.html",
        participantes=participantes,
        sala=sala,
        fecha=fecha,
        id_turno=id_turno,
        capacidad=capacidad,
        programa=programa
    )


@app.route('/salas', methods=['GET'])
def listar_salas():
    filtro_edificio = request.args.get("edificio")

    conexion = Conexion()

    # Edificios para el filtro
    conexion.cursor.execute("SELECT nombre_edificio FROM edificio")
    edificios = conexion.cursor.fetchall()

    # Query base
    if filtro_edificio:
        conexion.cursor.execute("""
            SELECT * FROM sala WHERE edificio = %s ORDER BY nombre_sala;
        """, (filtro_edificio,))
    else:
        conexion.cursor.execute("SELECT * FROM sala ORDER BY edificio, nombre_sala")

    salas = conexion.cursor.fetchall()
    conexion.cerrar()

    return render_template("salas_listado.html",
                           salas=salas,
                           edificios=edificios,
                           filtro_edificio=filtro_edificio)

@app.route('/salas/eliminar/<nombre_sala>', methods=['POST'])
def eliminar_sala(nombre_sala):

    conexion = Conexion()

    # 1) Obtener las reservas relacionadas a la sala
    conexion.cursor.execute("""
        SELECT id_reserva FROM reserva WHERE sala = %s;
    """, (nombre_sala,))
    reservas = conexion.cursor.fetchall()

    # 2) Borrar primero reserva_participante
    for r in reservas:
        conexion.cursor.execute("""
            DELETE FROM reserva_participante WHERE id_reserva = %s;
        """, (r["id_reserva"],))

    # 3) Ahora borrar las reservas
    conexion.cursor.execute("""
        DELETE FROM reserva WHERE sala = %s;
    """, (nombre_sala,))

    # 4) Finalmente, borrar la sala
    conexion.cursor.execute("""
        DELETE FROM sala WHERE nombre_sala = %s;
    """, (nombre_sala,))

    conexion.cnx.commit()
    conexion.cerrar()
    session.pop('flashes',None)
    flash(f"Sala {nombre_sala} eliminada correctamente.", "ok")
    return redirect(url_for("listar_salas"))

@app.route('/salas/editar/<nombre_sala>', methods=['GET'])
def formulario_editar_sala(nombre_sala):
    conexion = Conexion()

    # Sala
    conexion.cursor.execute("SELECT * FROM sala WHERE nombre_sala = %s", (nombre_sala,))
    sala = conexion.cursor.fetchone()

    # Edificios para combo
    conexion.cursor.execute("SELECT nombre_edificio FROM edificio")
    edificios = conexion.cursor.fetchall()

    conexion.cerrar()

    return render_template("salas_editar.html", sala=sala, edificios=edificios)

@app.route('/salas/editar/<nombre_sala>', methods=['POST'])
def editar_sala(nombre_sala):
    capacidad = request.form["capacidad"]
    tipo = request.form["tipo"]
    edificio = request.form["edificio"]

    conexion = Conexion()

    conexion.cursor.execute("""
        UPDATE sala
        SET capacidad = %s,
            tipo_sala = %s,
            edificio = %s
        WHERE nombre_sala = %s
    """, (capacidad, tipo, edificio, nombre_sala))

    conexion.cnx.commit()
    conexion.cerrar()
    session.pop('flashes',None)
    flash("Sala actualizada correctamente.", "ok")
    return redirect(url_for("listar_salas"))



# Ruta para listar programas académicos y mostrar formulario de inscripción
@app.route('/programas', methods=['GET'])
def form_participanteprograma():

    conexion = Conexion()

    # Obtener todos los programas
    conexion.cursor.execute("SELECT * FROM programa_academico")
    programas = conexion.cursor.fetchall()

    # Obtener programas donde el participante YA está inscripto
    ci = session.get("ci")
    conexion.cursor.execute("""
        SELECT nombre_programa 
        FROM participante_programa
        WHERE ci = %s
    """, (ci,))
    inscritos = {row["nombre_programa"] for row in conexion.cursor.fetchall()}

    conexion.cerrar()

    return render_template(
        "ParticipantePrograma_form.html",
        programas=programas,
        inscritos=inscritos
    )

@app.route('/reservas/mis_reservas')
def mis_reservas():
    ci = session.get("ci")
    if not ci:
        session.pop('flashes', None)
        flash("Debes iniciar sesión.", "error")
        return redirect(url_for('index'))

    conexion = Conexion()

    conexion.cursor.execute("""
        SELECT 
            r.id_reserva,
            r.fecha,
            r.estado,
            r.sala,
            r.nombre_edificio,
            t.hora_inicio,
            t.hora_final
        FROM reserva r
        JOIN reserva_participante rp ON rp.id_reserva = r.id_reserva
        JOIN turnos t ON t.id_turno = r.id_turno
        WHERE rp.ci = %s
        ORDER BY r.fecha DESC, r.id_reserva DESC;
    """, (ci,))

    reservas = conexion.cursor.fetchall()
    conexion.cerrar()

    return render_template("reservas_usuario.html", reservas=reservas)

@app.route('/reservas/cancelar/<int:id_reserva>', methods=['POST'])
def cancelar_reserva(id_reserva):

    conexion = Conexion()

    # Marcar la reserva como cancelada
    conexion.cursor.execute("""
        UPDATE reserva
        SET estado = 'Cancelada'
        WHERE id_reserva = %s;
    """, (id_reserva,))

    # También marcar asistencia como NULL o 0 en reserva_participante (opcional)
    conexion.cursor.execute("""
        UPDATE reserva_participante
        SET asistencia = NULL
        WHERE id_reserva = %s;
    """, (id_reserva,))

    conexion.cnx.commit()
    conexion.cerrar()
    session.pop('flashes',None)
    flash("Reserva cancelada correctamente.", "ok")
    return redirect(url_for("mis_reservas"))


@app.route('/mis_programas')
def mis_programas():
    ci = session.get("ci")
    if not ci:
        session.pop('flashes', None)
        flash("Debes iniciar sesión.", "error")
        return redirect(url_for("index"))

    conexion = Conexion()

    conexion.cursor.execute("""
        SELECT pa.nombre_programa, pr.tipo
        FROM participante_programa pa
        JOIN programa_academico pr ON pr.nombre_programa = pa.nombre_programa
        WHERE pa.ci = %s;
    """, (ci,))

    programas = conexion.cursor.fetchall()
    conexion.cerrar()

    return render_template("mis_programas.html", programas=programas)

@app.route('/mis_programas/<programa>/reservar')
def reservar_para_programa(programa):
    session["programa_reserva"] = programa
    return redirect(url_for('form_reserva'))

if __name__ == "__main__":
    app.run(debug=True)