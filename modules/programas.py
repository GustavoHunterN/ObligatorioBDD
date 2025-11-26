from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from Connector import Conexion
import control as cont

programas_bp = Blueprint('programas', __name__)


@programas_bp.route('/programas', methods=['GET'])
def form_participanteprograma():
    from modules.auth import require_login
    from flask_wtf.csrf import generate_csrf
    
    unauthorized = require_login()
    if unauthorized:
        return unauthorized

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
        inscritos=inscritos,
        csrf_token=generate_csrf
    )


@programas_bp.route('/mis_programas')
def mis_programas():
    from modules.auth import require_login
    unauthorized = require_login()
    if unauthorized:
        return unauthorized
    ci = session.get("ci")

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


@programas_bp.route('/mis_programas/<programa>/reservar')
def reservar_para_programa(programa):
    from modules.auth import require_login
    from modules.security import validate_programa_name
    
    unauthorized = require_login()
    if unauthorized:
        return unauthorized
    
    # Validate programa parameter
    programa = validate_programa_name(programa)
    
    ci = session.get("ci")
    conexion = Conexion()
    
    # Verificar que el usuario está en el programa usando JOIN
    if not cont.usuario_esta_en_programa(conexion, ci, programa):
        flash("No estás inscrito en este programa.", "error")
        conexion.cerrar()
        return redirect(url_for('programas.mis_programas'))
    
    conexion.cerrar()
    
    session["programa_reserva"] = programa
    tipo = request.args.get('tipo')
    # Validate tipo (whitelist)
    allowed_tipos = ['Grado', 'Posgrado']
    if tipo and tipo not in allowed_tipos:
        from flask import abort
        abort(400, f"Tipo de programa inválido. Permitidos: {allowed_tipos}")
    
    if tipo:
        session['tipo_programa'] = tipo
    return redirect(url_for('reservas.form_reserva'))

