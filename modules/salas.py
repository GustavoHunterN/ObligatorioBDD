from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from Connector import Conexion

salas_bp = Blueprint('salas', __name__)


@salas_bp.route('/salas', methods=['GET'])
def listar_salas():
    from modules.auth import require_admin
    from modules.security import validate_edificio_name
    
    unauthorized = require_admin()
    if unauthorized:
        return unauthorized
    
    filtro_edificio = request.args.get("edificio")
    # Validate edificio parameter if provided
    if filtro_edificio:
        filtro_edificio = validate_edificio_name(filtro_edificio)

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


@salas_bp.route('/salas/eliminar/<nombre_sala>', methods=['POST'])
def eliminar_sala(nombre_sala):
    from modules.auth import require_admin
    from modules.security import validate_sala_name
    
    unauthorized = require_admin()
    if unauthorized:
        return unauthorized
    
    # Validate sala name parameter
    nombre_sala = validate_sala_name(nombre_sala)

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
    flash(f"Sala {nombre_sala} eliminada correctamente.", "success")
    return redirect(url_for("salas.listar_salas"))


@salas_bp.route('/salas/editar/<nombre_sala>', methods=['GET'])
def formulario_editar_sala(nombre_sala):
    from modules.auth import require_admin
    from modules.security import validate_sala_name
    
    unauthorized = require_admin()
    if unauthorized:
        return unauthorized
    
    # Validate sala name parameter
    nombre_sala = validate_sala_name(nombre_sala)
    
    conexion = Conexion()

    # Sala
    conexion.cursor.execute("SELECT * FROM sala WHERE nombre_sala = %s", (nombre_sala,))
    sala = conexion.cursor.fetchone()

    # Edificios para combo
    conexion.cursor.execute("SELECT nombre_edificio FROM edificio")
    edificios = conexion.cursor.fetchall()

    conexion.cerrar()
    
    # Populate form with existing data
    from modules.forms import SalaEditForm
    form = SalaEditForm()
    form.capacidad.data = sala['capacidad']
    form.tipo.data = sala['tipo_sala']
    form.edificio.choices = [(e['nombre_edificio'], e['nombre_edificio']) for e in edificios]
    form.edificio.data = sala['edificio']

    return render_template("salas_editar.html", sala=sala, edificios=edificios, form=form)


@salas_bp.route('/salas/editar/<nombre_sala>', methods=['POST'])
def editar_sala(nombre_sala):
    from modules.auth import require_admin
    from modules.validation import sanitize_string, validate_alphanumeric
    from modules.security import validate_sala_name, validate_int_param, validate_edificio_name
    
    unauthorized = require_admin()
    if unauthorized:
        return unauthorized
    
    # Validate sala name parameter
    nombre_sala = validate_sala_name(nombre_sala)
    
    # Validate capacidad (must be positive integer)
    capacidad = validate_int_param(request.form.get("capacidad"), "capacidad", min_val=1, max_val=1000)
    
    # Validate tipo (whitelist)
    tipo = request.form.get("tipo", "")
    allowed_tipos = ['Docente', 'Posgrado', 'Libre']
    if tipo not in allowed_tipos:
        from flask import abort
        abort(400, f"Tipo de sala inválido. Permitidos: {allowed_tipos}")
    
    edificio = validate_edificio_name(request.form.get("edificio", ""))
    
    # Validar edificio
    is_valid, error = validate_alphanumeric(edificio, allow_spaces=False, allow_special=[])
    if not is_valid:
        flash(f"Edificio: {error}", "error")
        return redirect(url_for("salas.formulario_editar_sala", nombre_sala=nombre_sala))

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
    flash("Sala actualizada correctamente.", "success")
    return redirect(url_for("salas.listar_salas"))

