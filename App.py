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


@app.route('/alumno/home')
def dashboard_alumno():
    unauthorized = require_role("Alumno")

    if unauthorized:
        return unauthorized
    return f"""<h1>Alumno: {session['nombre']} {session['apellido']}</h1>
            <h2> Sesión iniciada con éxito</h2>
            {dict(session)}"""





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
    conexion = Conexion()
    object_temp = f'form_{nombre_clase.lower()}'

    if nombre_clase == "Reserva":

        # Obtener edificio desde sala
        edificio = cont.get_edificio_from_sala(conexion, data["sala"])
        if not edificio:
            conexion.cerrar()
            flash("No se pudo obtener el edificio de la sala seleccionada.", "error")
            return redirect(url_for("form_reserva"))

        # insertarlo en data ANTES de ordenar args
        data["edificio"] = edificio
        print('DATA RESERVA', data)

        # ⭐ VALIDAR RESTRICCIONES AQUÍ ⭐
        ok, msg = cont.restriccion_reserva(
            conexion,
            data["ci_sesion"],
            data["fecha"],
            data["sala"],
            session.get("rol"),
            session.get("tipo_programa")
        )
        if not ok:
            conexion.cerrar()
            flash(msg, "error")
            return redirect(url_for("form_reserva"))
        # ahora sí: usar ordenar_args
        args = cont.ordenar_args(nombre_clase, data)
        print("ARGS ORDENADOS (RESERVA):", args)

        # Crear el objeto con args correctos
        objeto = cont.create_objeto(nombre_clase, args)
        objeto.save(conexion)
        data["id_reserva"] = str(objeto.id_reserva)
        data["participante"] = data["ci_sesion"]
        rpargs = cont.ordenar_args("ReservaParticipante", data)
        rp = cont.create_objeto("ReservaParticipante",rpargs)
        print("OBJETO:", rp)
        rp.save(conexion)

        # Obtener lista de participantes (alumno o docente)
        lista_cis = cont.Reserva_Lista_participantes(data, request)

        print("LISTA DE PARTICIPANTES A INSERTAR:", lista_cis)

        for ci_part in lista_cis:
            data_rp = {
                "id_reserva": str(objeto.id_reserva),
                "participante": ci_part
            }

            rpargs = cont.ordenar_args("ReservaParticipante", data_rp)
            rp = cont.create_objeto("ReservaParticipante", rpargs)
            print("CREANDO RP:", rp)
            rp.save(conexion)

    elif nombre_clase == "Sala" and "cantidad" in data:
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

    else:
        args = cont.ordenar_args(nombre_clase, data)
        objeto = cont.create_objeto(nombre_clase, args)
        try:
            objeto.save(conexion)
        except IntegrityError:
            session.pop('flashes', None)
            flash("El objeto ya existe o viola una restricción única.", "error")
            return redirect(url_for(object_temp))
        except Exception as e:
            session.pop('flashes', None)
            flash(f"Error inesperado: {str(e)}", "error")
            return render_template('base.html')

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

    # --- BLOQUEAR RESERVA SI TIENE SANCIÓN ---
    if cont.tiene_sancion_activa(conexion, ci_sesion):
        salas = []  # para no romper el template
        turnos = []
        fecha = None

        flash("No puedes reservar salas porque tienes una sanción activa.", "error")
        conexion.cerrar()
        return render_template("reserva_form.html", salas=salas, turnos=turnos, fecha=fecha)

    edificios = cont.obtener_edificios(conexion)
    todos_los_turnos = cont.obtener_turnos(conexion)
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

    salas = cont.obtener_salas_filtradas(salas,
                                         session.get("rol"),
                                         session.get("tipo_programa")
                                         )

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
    id_turno = request.args.get("turno")
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

    conexion.cursor.execute("""
        SELECT p.ci, p.nombre, p.apellido
        FROM participante_programa pp
        JOIN participante p ON p.ci = pp.ci
        WHERE pp.nombre_programa = %s;
    """, (programa,))
    participantes = conexion.cursor.fetchall()

    participantes = [p for p in participantes if p["ci"] != ci]

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
    tipo = request.args.get('tipo')
    if tipo:
        session['tipo_programa'] = tipo
    return redirect(url_for('form_reserva'))


@app.route('/reservas/editar/<int:id_reserva>', methods=['GET'])
def editar_reserva_form(id_reserva):
    # Saber quién edita
    ci = session.get("ci")
    if not ci:
        flash("Debes iniciar sesión.", "error")
        return redirect(url_for('index'))

    conexion = Conexion()

    reserva = cont.obtener_reserva_por_id(conexion, id_reserva)

    if not reserva:
        flash("Reserva no encontrada.", "error")
        conexion.cerrar()
        return redirect(url_for('mis_reservas'))

    # No editar reservas canceladas
    if reserva["estado"] == "Cancelada":
        flash("No puedes editar una reserva cancelada.", "error")
        conexion.cerrar()
        return redirect(url_for('mis_reservas'))

    # Obtener participantes actuales
    participantes = cont.obtener_participantes_reserva(conexion, id_reserva)

    todos_los_turnos = cont.obtener_turnos(conexion)
    turnos = todos_los_turnos

    # === CARGAR SALAS (sin filtro de edificio) ===
    conexion.cursor.execute("SELECT * FROM sala;")
    salas_raw = conexion.cursor.fetchall()

    salas = cont.obtener_salas_filtradas(
        salas_raw,
        session.get("rol"),
        session.get("tipo_programa")
    )
    conexion.cerrar()

    return render_template(
        "reserva_editar.html",
        reserva=reserva,
        participantes=participantes,
        salas=salas,
        turnos=turnos,
        fecha=reserva["fecha"]
    )

@app.route('/reservas/editar/<int:id_reserva>', methods=['POST'])
def editar_reserva(id_reserva):
    ci = session.get("ci")
    if not ci:
        flash("Debes iniciar sesión.", "error")
        return redirect(url_for('index'))

    conexion = Conexion()

    # Armar data
    data = {
        "fecha": request.form.get("fecha"),
        "sala": request.form.get("sala"),
        "id_turno": request.form.get("id_turno"),
        "nombre_edificio": request.form.get("nombre_edificio"),
        "estado": request.form.get("estado"),
    }

    # ⭐ RESTRICCIONES ANTES DEL UPDATE
    ok, msg = cont.restriccion_reserva_editar(
        conexion,
        ci,
        data["fecha"],
        id_reserva,
        data["sala"],
        session.get("rol"),
        session.get("tipo_programa")
    )
    if not ok:
        flash(msg, "error")
        conexion.cerrar()
        return redirect(url_for('mis_reservas'))

    # ⭐ COMPROBAR PISADO
    if cont.turno_ocupado_en_edicion(
            conexion,
            data["sala"],
            data["nombre_edificio"],
            data["fecha"],
            data["id_turno"],
            id_reserva
    ):
        flash("Ese turno ya está ocupado.", "error")
        conexion.cerrar()
        return redirect(url_for("mis_reservas"))

    # ---- si pasa la restricción, recién aquí updateas ----

    conexion.cursor.execute("""
        UPDATE reserva
        SET fecha = %s, sala = %s, id_turno = %s, nombre_edificio = %s, estado = %s
        WHERE id_reserva = %s
    """, (
        data["fecha"],
        data["sala"],
        data["id_turno"],
        data["nombre_edificio"],
        data["estado"],
        id_reserva
    ))

    conexion.cnx.commit()
    conexion.cerrar()

    flash("Reserva actualizada correctamente.", "success")
    return redirect(url_for("mis_reservas"))


@app.route('/reservas/<int:id_reserva>/asistencia', methods=['GET'])
def pasar_lista(id_reserva):
    if session.get("rol") != "Docente":
        flash("Acceso no autorizado.", "error")
        return redirect(url_for("mis_reservas"))
    conexion = Conexion()
    # 1. Verificar si nadie asistió
    if cont.ninguno_asistio(conexion, id_reserva):

        participantes = cont.participantes_de_reserva(conexion, id_reserva)

        # 2. Crear sanciones
        for ci_part in participantes:
            sancion = cont.create_objeto("Sancion",ci_part)
            sancion.save(conexion)

        flash("Se aplicó una sanción de 2 meses por inasistencia total.", "error")

    conexion = Conexion()

    # Obtener reserva
    reserva = cont.obtener_reserva_por_id(conexion, id_reserva)
    if not reserva:
        flash("Reserva no encontrada.", "error")
        conexion.cerrar()
        return redirect(url_for("mis_reservas"))

    # Traer participantes de esta reserva
    participantes = cont.obtener_participantes_reserva_detallado(conexion, id_reserva)

    conexion.cerrar()

    return render_template(
        "asistencia_reserva.html",
        reserva=reserva,
        participantes=participantes
    )



@app.route('/reservas/<int:id_reserva>/asistencia', methods=['POST'])
def guardar_asistencia(id_reserva):
    if session.get("rol") != "Docente":
        flash("Acceso no autorizado.", "error")
        return redirect(url_for("mis_reservas"))

    conexion = Conexion()

    # Obtener participantes
    conexion.cursor.execute("""
        SELECT ci
        FROM reserva_participante
        WHERE id_reserva = %s;
    """, (id_reserva,))
    participantes = conexion.cursor.fetchall()

    for p in participantes:
        ci = p["ci"]
        key = f"asistencia_{ci}"
        asistencia = 1 if key in request.form else 0

        conexion.cursor.execute("""
            UPDATE reserva_participante
            SET asistencia = %s
            WHERE id_reserva = %s AND ci = %s;
        """, (asistencia, id_reserva, ci))

    conexion.cnx.commit()
    conexion.cerrar()

    flash("Asistencia registrada correctamente.", "success")
    return redirect(url_for("mis_reservas"))


# -------------------- USUARIOS (ADMIN) --------------------

@app.route('/usuarios', methods=['GET'])
def listar_usuarios():
    if session.get("rol") != "Admin":
        flash("Acceso no autorizado.", "error")
        return redirect(url_for("index"))

    conexion = Conexion()
    conexion.cursor.execute("""
        SELECT ci, nombre, apellido, correo, rol
        FROM participante
        ORDER BY apellido, nombre;
    """)
    usuarios = conexion.cursor.fetchall()
    conexion.cerrar()

    return render_template("usuarios_listado.html", usuarios=usuarios)


@app.route('/usuarios/editar/<ci>', methods=['GET'])
def editar_usuario_form(ci):
    if session.get("rol") != "Admin":
        flash("Acceso no autorizado.", "error")
        return redirect(url_for("index"))

    conexion = Conexion()
    conexion.cursor.execute("""
        SELECT ci, nombre, apellido, correo, rol
        FROM participante
        WHERE ci = %s;
    """, (ci,))
    usuario = conexion.cursor.fetchone()
    conexion.cerrar()

    if not usuario:
        flash("Usuario no encontrado.", "error")
        return redirect(url_for("listar_usuarios"))

    return render_template("usuario_editar.html", usuario=usuario)


@app.route('/usuarios/editar/<ci>', methods=['POST'])
def editar_usuario(ci):
    if session.get("rol") != "Admin":
        flash("Acceso no autorizado.", "error")
        return redirect(url_for("index"))

    nombre = request.form.get("nombre")
    apellido = request.form.get("apellido")
    correo = request.form.get("correo")
    rol = request.form.get("rol")

    conexion = Conexion()
    conexion.cursor.execute("""
        UPDATE participante
        SET nombre = %s, apellido = %s, correo = %s, rol = %s
        WHERE ci = %s;
    """, (nombre, apellido, correo, rol, ci))

    conexion.cnx.commit()
    conexion.cerrar()

    flash("Usuario actualizado correctamente.", "ok")
    return redirect(url_for("listar_usuarios"))


@app.route('/usuarios/eliminar/<ci>', methods=['POST'])
def eliminar_usuario(ci):
    if session.get("rol") != "Admin":
        flash("Acceso no autorizado.", "error")
        return redirect(url_for("index"))

    conexion = Conexion()

    # Borrar relaciones primero
    conexion.cursor.execute("DELETE FROM participante_programa WHERE ci = %s;", (ci,))
    conexion.cursor.execute("DELETE FROM reserva_participante WHERE ci = %s;", (ci,))

    # No se borran las reservas, solo se desvincula al usuario
    conexion.cursor.execute("DELETE FROM sancion_participante WHERE ci = %s;", (ci,))

    # Finalmente borrar el usuario
    conexion.cursor.execute("DELETE FROM participante WHERE ci = %s;", (ci,))

    conexion.cnx.commit()
    conexion.cerrar()

    flash("Usuario eliminado correctamente.", "ok")
    return redirect(url_for("listar_usuarios"))

# -------------------- SANCIONES (ADMIN / DOCENTE) --------------------

@app.route('/sanciones', methods=['GET'])
def listar_sanciones():
    # Solo docentes (o BI) pueden editar sanciones
   # if session.get("rol") != "Admin":
    #    flash("Acceso no autorizado.", "error")
     #   return redirect(url_for("index"))

    conexion = Conexion()
    sanciones = cont.obtener_sanciones(conexion)
    conexion.cerrar()

    return render_template("sanciones_listado.html", sanciones=sanciones)


@app.route('/sanciones/editar/<int:id_sancion>', methods=['GET'])
def editar_sancion_form(id_sancion):
    if session.get("rol") != "Admin":
        flash("Acceso no autorizado.", "error")
        return redirect(url_for("index"))

    conexion = Conexion()
    sancion = cont.obtener_sancion_por_id(conexion, id_sancion)
    conexion.cerrar()

    if not sancion:
        flash("Sanción no encontrada.", "error")
        return redirect(url_for("listar_sanciones"))

    return render_template("sancion_editar.html", sancion=sancion)


@app.route('/sanciones/editar/<int:id_sancion>', methods=['POST'])
def editar_sancion(id_sancion):
    if session.get("rol") != "Admin":
        flash("Acceso no autorizado.", "error")
        return redirect(url_for("index"))

    fecha_final = request.form.get("fecha_final")
    if not fecha_final:
        flash("Debes ingresar una fecha final.", "error")
        return redirect(url_for("editar_sancion_form", id_sancion=id_sancion))

    conexion = Conexion()
    cont.actualizar_sancion(conexion, id_sancion, fecha_final)
    conexion.cnx.commit()
    conexion.cerrar()

    flash("Sanción actualizada correctamente.", "success")
    return redirect(url_for("listar_sanciones"))


@app.route('/sanciones/eliminar/<int:id_sancion>', methods=['POST'])
def eliminar_sancion(id_sancion):
    if session.get("rol") != "Admin":
       flash("Acceso no autorizado.", "error")
       return redirect(url_for("index"))

    conexion = Conexion()
    cont.eliminar_sancion(conexion, id_sancion)
    conexion.cnx.commit()
    conexion.cerrar()

    flash("Sanción eliminada correctamente.", "ok")
    return redirect(url_for("listar_sanciones"))

# -------------------- MÓDULO BI / REPORTES --------------------

@app.route('/bi')
def bi_menu():
    if session.get("rol") not in ("Docente", "Admin"):
        flash("Acceso no autorizado al módulo BI.", "error")
        return redirect(url_for("index"))

    return render_template("bi/menu.html")

@app.route('/bi/salas_mas_reservadas')
def bi_salas_mas_reservadas():
    conexion = Conexion()
    conexion.cursor.execute("""
        SELECT sala, COUNT(*) AS total
        FROM reserva
        GROUP BY sala
        ORDER BY total DESC;
    """)
    rows = conexion.cursor.fetchall()
    conexion.cerrar()

    return render_template("bi/tabla.html",
                           titulo="Salas más reservadas",
                           datos=rows,
                           columnas=["sala", "total"])

@app.route('/bi/turnos_mas_demandados')
def bi_turnos_mas_demandados():
    conexion = Conexion()
    conexion.cursor.execute("""
        SELECT t.hora_inicio, t.hora_final, COUNT(*) AS total
        FROM reserva r
        JOIN turnos t ON r.id_turno = t.id_turno
        GROUP BY r.id_turno
        ORDER BY total DESC;
    """)
    rows = conexion.cursor.fetchall()
    conexion.cerrar()

    return render_template("bi/tabla.html",
                           titulo="Turnos más demandados",
                           datos=rows,
                           columnas=["hora_inicio", "hora_final", "total"])

@app.route('/bi/promedio_participantes_sala')
def bi_promedio_participantes_sala():
    conexion = Conexion()
    conexion.cursor.execute("""
        SELECT r.sala, AVG(sub.cant) AS promedio
        FROM reserva r
        JOIN (
            SELECT id_reserva, COUNT(*) AS cant
            FROM reserva_participante
            GROUP BY id_reserva
        ) sub ON sub.id_reserva = r.id_reserva
        GROUP BY r.sala;
    """)
    rows = conexion.cursor.fetchall()
    conexion.cerrar()

    return render_template("bi/tabla.html",
                           titulo="Promedio de participantes por sala",
                           datos=rows,
                           columnas=["sala", "promedio"])

@app.route('/bi/reservas_por_carrera_facultad')
def bi_reservas_por_carrera_facultad():
    conexion = Conexion()
    conexion.cursor.execute("""
        SELECT pa.nombre_programa,
               f.nombre AS facultad,
               COUNT(*) AS total
        FROM reserva_participante rp
        JOIN participante_programa pp ON pp.ci = rp.ci
        JOIN programa_academico pa ON pa.nombre_programa = pp.nombre_programa
        JOIN facultad f ON f.nombre = pa.nombre_facultad
        GROUP BY pa.nombre_programa, f.nombre;
    """)
    rows = conexion.cursor.fetchall()
    conexion.cerrar()

    return render_template("bi/tabla.html",
                           titulo="Reservas por carrera y facultad",
                           datos=rows,
                           columnas=["programa","facultad","total"])


@app.route('/bi/ocupacion_por_edificio')
def bi_ocupacion_por_edificio():
    conexion = Conexion()
    conexion.cursor.execute("""
        SELECT nombre_edificio,
               COUNT(*) AS reservas
        FROM reserva
        GROUP BY nombre_edificio;
    """)
    reservas = conexion.cursor.fetchall()

    conexion.cursor.execute("SELECT COUNT(*) AS total FROM sala;")
    total_salas = conexion.cursor.fetchone()["total"]

    for r in reservas:
        r["porcentaje"] = round((r["reservas"] / total_salas) * 100, 2)

    conexion.cerrar()

    return render_template("bi/tabla.html",
                           titulo="Porcentaje de ocupación de salas por edificio",
                           datos=reservas,
                           columnas=["nombre_edificio","reservas","porcentaje"])

@app.route('/bi/reservas_asistencias_por_rol')
def bi_reservas_asistencias_por_rol():
    conexion = Conexion()
    conexion.cursor.execute("""
        SELECT p.rol,
               pr.tipo AS tipo_programa,
               COUNT(DISTINCT rp.id_reserva) AS reservas,
               SUM(CASE WHEN rp.asistencia = 1 THEN 1 ELSE 0 END) AS asistencias
        FROM participante p
        JOIN participante_programa prg ON prg.ci = p.ci
        JOIN programa_academico pr ON pr.nombre_programa = prg.nombre_programa
        JOIN reserva_participante rp ON rp.ci = p.ci
        GROUP BY p.rol, pr.tipo;
    """)
    rows = conexion.cursor.fetchall()
    conexion.cerrar()

    return render_template("bi/tabla.html",
                           titulo="Reservas y asistencias por rol y tipo",
                           datos=rows,
                           columnas=["rol","tipo_programa","reservas","asistencias"])

@app.route('/bi/sanciones_por_rol')
def bi_sanciones_por_rol():
    conexion = Conexion()
    conexion.cursor.execute("""
        SELECT 
            p.rol,
            COUNT(*) AS sanciones
        FROM sancion_participante sp
        JOIN participante p ON p.ci = sp.ci
        GROUP BY p.rol;
    """)
    rows = conexion.cursor.fetchall()
    conexion.cerrar()

    return render_template("bi/tabla.html",
                           titulo="Sanciones por rol",
                           datos=rows,
                           columnas=["rol","sanciones"])


@app.route('/bi/porcentaje_uso')
def bi_porcentaje_uso():
    conexion = Conexion()

    conexion.cursor.execute("SELECT COUNT(*) AS total FROM reserva;")
    total = conexion.cursor.fetchone()["total"]

    conexion.cursor.execute("SELECT COUNT(*) AS usadas FROM reserva WHERE estado = 'Activa';")
    usadas = conexion.cursor.fetchone()["usadas"]

    porcentaje = round((usadas / total) * 100, 2) if total else 0

    conexion.cerrar()

    return render_template("bi/tabla.html",
                           titulo="Porcentaje de reservas efectivamente utilizadas",
                           datos=[{"total": total, "usadas": usadas, "porcentaje": porcentaje}],
                           columnas=["total","usadas","porcentaje"])


@app.route('/bi/top_usuarios')
def bi_top_usuarios():
    conexion = Conexion()
    conexion.cursor.execute("""
        SELECT p.ci, p.nombre, p.apellido, COUNT(*) AS reservas
        FROM reserva_participante rp
        JOIN participante p ON p.ci = rp.ci
        GROUP BY rp.ci
        ORDER BY reservas DESC
        LIMIT 5;
    """)
    rows = conexion.cursor.fetchall()
    conexion.cerrar()

    return render_template("bi/tabla.html",
                           titulo="Top 5 usuarios con más reservas",
                           datos=rows,
                           columnas=["ci","nombre","apellido","reservas"])


@app.route('/bi/edificios_por_programa')
def bi_edificios_por_programa():
    conexion = Conexion()
    conexion.cursor.execute("""
        SELECT pr.tipo AS tipo_programa,
               r.nombre_edificio,
               COUNT(*) AS total
        FROM reserva r
        JOIN reserva_participante rp ON rp.id_reserva = r.id_reserva
        JOIN participante_programa pp ON pp.ci = rp.ci
        JOIN programa_academico pr ON pr.nombre_programa = pp.nombre_programa
        GROUP BY pr.tipo, r.nombre_edificio
        ORDER BY total DESC;
    """)
    rows = conexion.cursor.fetchall()
    conexion.cerrar()

    return render_template("bi/tabla.html",
                           titulo="Uso de edificios por tipo de programa",
                           datos=rows,
                           columnas=["tipo_programa","nombre_edificio","total"])

@app.route('/bi/capacidad_promedio')
def bi_capacidad_promedio():
    conexion = Conexion()
    conexion.cursor.execute("""
        SELECT s.nombre_sala,
               s.capacidad,
               AVG(sub.cant) AS ocupacion_promedio
        FROM sala s
        JOIN reserva r ON r.sala = s.nombre_sala
        JOIN (
            SELECT id_reserva, COUNT(*) AS cant
            FROM reserva_participante
            GROUP BY id_reserva
        ) sub ON sub.id_reserva = r.id_reserva
        GROUP BY s.nombre_sala, s.capacidad;
    """)
    rows = conexion.cursor.fetchall()
    conexion.cerrar()

    return render_template("bi/tabla.html",
                           titulo="Ocupación promedio vs capacidad",
                           datos=rows,
                           columnas=["nombre_sala","capacidad","ocupacion_promedio"])


@app.route('/reservas', methods=['GET'])
def reservas_por_usuario():
    if session.get("rol") != "Admin":
        flash("Acceso no autorizado.", "error")
        return redirect(url_for("index"))

    ci = request.args.get("ci")

    if not ci:
        flash("Debe especificar un CI.", "error")
        return redirect(url_for("listar_usuarios"))

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
        ORDER BY r.fecha DESC;
    """, (ci,))

    reservas = conexion.cursor.fetchall()
    conexion.cerrar()

    return render_template("reservas_admin.html", reservas=reservas, ci=ci)


@app.route('/usuarios/<ci>/programas', methods=['GET'])
def programas_de_usuario(ci):
    if session.get("rol") != "Admin":
        flash("Acceso no autorizado.", "error")
        return redirect(url_for("index"))

    conexion = Conexion()
    conexion.cursor.execute("""
        SELECT 
            pp.nombre_programa,
            pr.tipo,
            pr.nombre_facultad
        FROM participante_programa pp
        JOIN programa_academico pr ON pr.nombre_programa = pp.nombre_programa
        WHERE pp.ci = %s
        ORDER BY pp.nombre_programa;
    """, (ci,))
    programas = conexion.cursor.fetchall()
    conexion.cerrar()

    return render_template("usuario_programas.html", ci=ci, programas=programas)

@app.route('/usuarios/<ci>/programas/eliminar', methods=['POST'])
def eliminar_usuario_de_programa(ci):
    if session.get("rol") != "Admin":
        flash("Acceso no autorizado.", "error")
        return redirect(url_for("index"))

    programa = request.form.get("programa")

    if not programa:
        flash("Programa no especificado.", "error")
        return redirect(url_for("programas_de_usuario", ci=ci))

    conexion = Conexion()
    conexion.cursor.execute("""
        DELETE FROM participante_programa
        WHERE ci = %s AND nombre_programa = %s;
    """, (ci, programa))
    conexion.cnx.commit()
    conexion.cerrar()

    flash(f"El usuario fue dado de baja del programa {programa}.", "ok")
    return redirect(url_for("programas_de_usuario", ci=ci))

if __name__ == "__main__":
    app.run(debug=True)

