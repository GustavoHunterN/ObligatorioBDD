from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from Connector import Conexion

auth_bp = Blueprint('auth_bp', __name__)

def require_role(role: str):
    """Middleware simple para validar acceso por rol."""
    if session.get("rol") != role:
        flash("Acceso no autorizado.", "error")
        return redirect(url_for(f'login_{role.lower()}_form'))


# ------------------------------------------
#ALUMNO
# ------------------------------------------
@auth_bp.route('/login/alumno', methods=['GET'])
def login_alumno_form():
    session.pop('_flashes', None)
    return render_template('login_alumno.html')

@auth_bp.route('/login/alumno', methods=['POST'])
def login_alumno():
    correo = request.form.get('correo')
    contrasena = request.form.get('contrasena')
    print("== LOGIN ALUMNO ==")
    print("correo:", correo)
    print("pass:", contrasena)

    if not (correo and contrasena):
        flash("Debes ingresar correo y contraseña.", "login_error")
        return redirect(url_for('login_alumno_form'))

    # --- LOGIN ADMIN --------------------
    conexion = Conexion()
    conexion.cursor.execute("""
        SELECT p.ci, p.nombre, p.apellido, p.correo
        FROM participante p
        JOIN login l ON l.correo = p.correo
        WHERE l.correo = %s
          AND l.contrasena = %s
          AND p.rol = 'Admin'
        LIMIT 1;
    """, (correo, contrasena))

    admin = conexion.cursor.fetchone()

    if admin:
        session["ci"] = admin["ci"]
        session["nombre"] = admin["nombre"]
        session["apellido"] = admin["apellido"]
        session["correo"] = admin["correo"]
        session["rol"] = "Admin"
        flash(f"Bienvenido, {admin['nombre']} (Admin)", "ok")
        conexion.cerrar()
        return redirect(url_for("bi_menu"))
    # ----------------------------------
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


# ------------------------------------------
#DOCENTE
# ------------------------------------------
@auth_bp.route('/login/docente', methods=['GET'])
def login_docente_form():
    session.pop('_flashes', None)
    return render_template('login_docente.html')

@auth_bp.route('/login/docente', methods=['POST'])
def login_docente():
    correo = request.form.get('correo')
    contrasena = request.form.get('contrasena')
    print("== LOGIN DOCENTE ==")
    print("correo:", correo)
    print("pass:", contrasena)


    if not (correo and contrasena):
        flash("Debes ingresar correo y contraseña.", "login_error")
        return redirect(url_for('login_docente_form'))

    # --- LOGIN ADMIN --------------------
    conexion = Conexion()
    conexion.cursor.execute("""
        SELECT p.ci, p.nombre, p.apellido, p.correo
        FROM participante p
        JOIN login l ON l.correo = p.correo
        WHERE l.correo = %s
          AND l.contrasena = %s
          AND p.rol = 'Admin'
        LIMIT 1;
    """, (correo, contrasena))

    admin = conexion.cursor.fetchone()

    if admin:
        session["ci"] = admin["ci"]
        session["nombre"] = admin["nombre"]
        session["apellido"] = admin["apellido"]
        session["correo"] = admin["correo"]
        session["rol"] = "Admin"
        flash(f"Bienvenido, {admin['nombre']} (Admin)", "ok")
        conexion.cerrar()
        return redirect(url_for("bi_menu"))

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



