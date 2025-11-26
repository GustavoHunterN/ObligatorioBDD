from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import datetime
import control as cont
from Connector import Conexion

reservas_bp = Blueprint('reservas', __name__)


@reservas_bp.route('/reserva/crear', methods=['GET'])
def form_reserva():
    from modules.auth import require_login
    unauthorized = require_login()
    if unauthorized:
        return unauthorized
    
    # ⭐ REQUERIR QUE SE SELECCIONE UN PROGRAMA PRIMERO ⭐
    programa = session.get("programa_reserva")
    if not programa:
        flash("Debes seleccionar un programa antes de crear una reserva.", "error")
        return redirect(url_for('programas.mis_programas'))
    
    ci_sesion = session.get("ci")
    fecha = request.args.get("fecha")
    if not fecha:
        fecha = datetime.date.today()
    else:
        from modules.security import validate_date_string
        fecha = validate_date_string(fecha, "fecha")
        fecha = datetime.datetime.strptime(fecha, "%Y-%m-%d").date()
    
    filtro_edificio = request.args.get("edificio")
    if filtro_edificio:
        from modules.security import validate_edificio_name
        filtro_edificio = validate_edificio_name(filtro_edificio)
    
    filtro_turno = request.args.get("id_turno")
    if filtro_turno:
        from modules.security import validate_int_param
        filtro_turno = validate_int_param(filtro_turno, "id_turno", min_val=1)
    
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
    
    # Obtener tipo de programa para mostrar
    conexion = Conexion()
    conexion.cursor.execute("""
        SELECT tipo FROM programa_academico WHERE nombre_programa = %s
    """, (programa,))
    programa_info = conexion.cursor.fetchone()
    tipo_programa = programa_info["tipo"] if programa_info else None
    conexion.cerrar()
    
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
        fecha_hoy = fecha_hoy,
        programa=programa,
        tipo_programa=tipo_programa
    )


@reservas_bp.route('/reserva/participantes')
def seleccionar_participantes():
    from modules.auth import require_login
    unauthorized = require_login()
    if unauthorized:
        return unauthorized
    ci = session.get("ci")
    rol = session.get("rol")
    programa = session.get("programa_reserva")

    if not ci or not programa:
        flash("Debe seleccionar un programa antes de reservar.", "error")
        return redirect(url_for('programas.mis_programas'))

    sala = request.args.get("sala")
    if sala:
        from modules.security import validate_sala_name
        sala = validate_sala_name(sala)
    
    id_turno = request.args.get("turno")
    if id_turno:
        from modules.security import validate_int_param
        id_turno = validate_int_param(id_turno, "turno", min_val=1)
    
    fecha = request.args.get("fecha")
    if fecha:
        from modules.security import validate_date_string
        fecha = validate_date_string(fecha, "fecha")

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
        return redirect(url_for("reservas.form_reserva"))

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
            return redirect(url_for('reservas.form_reserva'))

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


@reservas_bp.route('/reservas/mis_reservas')
def mis_reservas():
    from modules.auth import require_login
    unauthorized = require_login()
    if unauthorized:
        return unauthorized
    ci = session.get("ci")

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


@reservas_bp.route('/reservas/cancelar/<int:id_reserva>', methods=['POST'])
def cancelar_reserva(id_reserva):
    from modules.auth import require_login
    from modules.security import validate_int_param
    
    unauthorized = require_login()
    if unauthorized:
        return unauthorized
    
    # Validate id_reserva parameter
    id_reserva = validate_int_param(id_reserva, "id_reserva", min_val=1)

    ci = session.get("ci")
    conexion = Conexion()

    # Verificar que el usuario es participante de la reserva usando JOIN
    if not cont.usuario_es_participante_reserva(conexion, ci, id_reserva):
        flash("No tienes permiso para cancelar esta reserva.", "error")
        conexion.cerrar()
        return redirect(url_for("reservas.mis_reservas"))

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
    flash("Reserva cancelada correctamente.", "success")
    return redirect(url_for("reservas.mis_reservas"))


@reservas_bp.route('/reservas/editar/<int:id_reserva>', methods=['GET'])
def editar_reserva_form(id_reserva):
    from modules.auth import require_login
    from modules.security import validate_int_param
    
    unauthorized = require_login()
    if unauthorized:
        return unauthorized
    
    # Validate id_reserva parameter
    id_reserva = validate_int_param(id_reserva, "id_reserva", min_val=1)
    
    ci = session.get("ci")

    conexion = Conexion()

    reserva = cont.obtener_reserva_por_id(conexion, id_reserva)

    if not reserva:
        flash("Reserva no encontrada.", "error")
        conexion.cerrar()
        return redirect(url_for('reservas.mis_reservas'))

    # Verificar que el usuario es participante de la reserva usando JOIN
    if not cont.usuario_es_participante_reserva(conexion, ci, id_reserva):
        flash("No tienes permiso para editar esta reserva.", "error")
        conexion.cerrar()
        return redirect(url_for('reservas.mis_reservas'))

    # No editar reservas canceladas
    if reserva["estado"] == "Cancelada":
        flash("No puedes editar una reserva cancelada.", "error")
        conexion.cerrar()
        return redirect(url_for('reservas.mis_reservas'))

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
    
    # Get edificios for form
    conexion.cursor.execute("SELECT nombre_edificio FROM edificio;")
    edificios_raw = conexion.cursor.fetchall()
    conexion.cerrar()
    
    # Populate form with existing data
    from modules.forms import ReservaEditForm
    from datetime import datetime
    
    form = ReservaEditForm()
    form.sala.choices = [(s['nombre_sala'], s['nombre_sala']) for s in salas]
    form.id_turno.choices = [(str(t['id_turno']), f"{t['hora_inicio']} - {t['hora_final']}") for t in turnos]
    form.nombre_edificio.choices = [(e['nombre_edificio'], e['nombre_edificio']) for e in edificios_raw]
    
    # Set current values
    form.fecha.data = reserva['fecha']
    form.sala.data = reserva['sala']
    form.id_turno.data = str(reserva['id_turno'])
    form.nombre_edificio.data = reserva['nombre_edificio']
    form.estado.data = reserva['estado']

    return render_template(
        "reserva_editar.html",
        reserva=reserva,
        participantes=participantes,
        salas=salas,
        turnos=turnos,
        fecha=reserva["fecha"],
        form=form
    )


@reservas_bp.route('/reservas/editar/<int:id_reserva>', methods=['POST'])
def editar_reserva(id_reserva):
    from modules.auth import require_login
    from modules.security import validate_int_param
    
    unauthorized = require_login()
    if unauthorized:
        return unauthorized
    
    # Validate id_reserva parameter
    id_reserva = validate_int_param(id_reserva, "id_reserva", min_val=1)
    
    ci = session.get("ci")

    conexion = Conexion()

    # Verificar que el usuario es participante de la reserva usando JOIN
    if not cont.usuario_es_participante_reserva(conexion, ci, id_reserva):
        flash("No tienes permiso para editar esta reserva.", "error")
        conexion.cerrar()
        return redirect(url_for('reservas.mis_reservas'))

    from modules.forms import ReservaEditForm
    
    # Get choices for form
    todos_los_turnos = cont.obtener_turnos(conexion)
    conexion.cursor.execute("SELECT * FROM sala;")
    salas_raw = conexion.cursor.fetchall()
    conexion.cursor.execute("SELECT nombre_edificio FROM edificio;")
    edificios_raw = conexion.cursor.fetchall()
    
    form = ReservaEditForm()
    form.sala.choices = [(s['nombre_sala'], s['nombre_sala']) for s in salas_raw]
    form.id_turno.choices = [(str(t['id_turno']), f"{t['hora_inicio']} - {t['hora_final']}") for t in todos_los_turnos]
    form.nombre_edificio.choices = [(e['nombre_edificio'], e['nombre_edificio']) for e in edificios_raw]
    
    if not form.validate_on_submit():
        # Flash validation errors
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field}: {error}", "error")
        conexion.cerrar()
        return redirect(url_for('reservas.mis_reservas'))
    
    # El edificio NO se puede cambiar - mantener el edificio original de la reserva
    # Obtener el edificio original de la reserva
    conexion.cursor.execute("""
        SELECT nombre_edificio FROM reserva WHERE id_reserva = %s
    """, (id_reserva,))
    reserva_original = conexion.cursor.fetchone()
    
    if not reserva_original:
        flash("Reserva no encontrada.", "error")
        conexion.cerrar()
        return redirect(url_for('reservas.mis_reservas'))
    
    # Usar el edificio original (no el que viene del formulario)
    edificio_original = reserva_original["nombre_edificio"]
    sala_actual = form.sala.data
    
    # Armar data from form - mantener edificio y sala originales
    data = {
        "fecha": form.fecha.data.strftime('%Y-%m-%d'),
        "sala": sala_actual,
        "id_turno": str(form.id_turno.data),
        "nombre_edificio": edificio_original,  # Mantener edificio original
        "estado": form.estado.data,
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
        return redirect(url_for('reservas.mis_reservas'))

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
        return redirect(url_for("reservas.mis_reservas"))

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
    return redirect(url_for("reservas.mis_reservas"))


@reservas_bp.route('/reservas/<int:id_reserva>/asistencia', methods=['GET'])
def pasar_lista(id_reserva):
    from modules.auth import require_role
    from modules.security import validate_int_param
    
    unauthorized = require_role("Docente")
    if unauthorized:
        return unauthorized
    
    # Validate id_reserva parameter
    id_reserva = validate_int_param(id_reserva, "id_reserva", min_val=1)
    
    ci = session.get("ci")
    conexion = Conexion()

    # Obtener reserva
    reserva = cont.obtener_reserva_por_id(conexion, id_reserva)
    if not reserva:
        flash("Reserva no encontrada.", "error")
        conexion.cerrar()
        return redirect(url_for("reservas.mis_reservas"))

    # Verificar que el usuario es participante de la reserva usando JOIN
    if not cont.usuario_es_participante_reserva(conexion, ci, id_reserva):
        flash("No tienes permiso para acceder a esta reserva.", "error")
        conexion.cerrar()
        return redirect(url_for("reservas.mis_reservas"))

    # Traer participantes de esta reserva
    participantes = cont.obtener_participantes_reserva_detallado(conexion, id_reserva)

    conexion.cerrar()

    return render_template(
        "asistencia_reserva.html",
        reserva=reserva,
        participantes=participantes
    )


@reservas_bp.route('/reservas/<int:id_reserva>/asistencia', methods=['POST'])
def guardar_asistencia(id_reserva):
    from modules.auth import require_role
    from modules.security import validate_int_param, validate_ci
    
    unauthorized = require_role("Docente")
    if unauthorized:
        return unauthorized
    
    # Validate id_reserva parameter
    id_reserva = validate_int_param(id_reserva, "id_reserva", min_val=1)

    ci = session.get("ci")
    conexion = Conexion()

    # Verificar que el usuario es participante de la reserva usando JOIN
    if not cont.usuario_es_participante_reserva(conexion, ci, id_reserva):
        flash("No tienes permiso para acceder a esta reserva.", "error")
        conexion.cerrar()
        return redirect(url_for("reservas.mis_reservas"))

    # Obtener participantes
    conexion.cursor.execute("""
        SELECT ci
        FROM reserva_participante
        WHERE id_reserva = %s;
    """, (id_reserva,))
    participantes = conexion.cursor.fetchall()

    # Guardar asistencia de cada participante
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

    # Verificar si nadie asistió DESPUÉS de guardar la asistencia
    if cont.ninguno_asistio(conexion, id_reserva):
        participantes_reserva = cont.participantes_de_reserva(conexion, id_reserva)
        sanciones_aplicadas = 0
        sanciones_duplicadas = []
        for ci_part in participantes_reserva:
            sancion = cont.create_objeto("Sancion", ci_part)
            try:
                sancion.save(conexion)
                sanciones_aplicadas += 1
            except ValueError as e:
                sanciones_duplicadas.append(ci_part)

        if sanciones_duplicadas:
            flash(f"Se aplicaron {sanciones_aplicadas} sanciones. Los siguientes participantes ya tenían sanción activa: {', '.join(sanciones_duplicadas)}", "warning")
        else:
            flash(f"Se aplicó una sanción de 2 meses por inasistencia total a {sanciones_aplicadas} participante(s).", "error")
    else:
        flash("Asistencia registrada correctamente.", "success")

    conexion.cerrar()
    return redirect(url_for("reservas.mis_reservas"))


@reservas_bp.route('/reservas', methods=['GET'])
def reservas_por_usuario():
    from modules.auth import require_admin
    unauthorized = require_admin()
    if unauthorized:
        return unauthorized

    from modules.security import validate_ci
    
    ci = request.args.get("ci")
    if not ci:
        flash("Debe especificar un CI.", "error")
        return redirect(url_for("usuarios.listar_usuarios"))
    
    # Validate CI parameter
    ci = validate_ci(ci)

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

