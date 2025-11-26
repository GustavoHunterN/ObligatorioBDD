from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from Connector import Conexion

auth_bp = Blueprint('auth_bp', __name__)

def require_role(role: str):
    """Middleware simple para validar acceso por rol."""
    if session.get("rol") != role:
        flash("Acceso no autorizado.", "error")
        return redirect(url_for(f'auth_bp.login_{role.lower()}_form'))


def require_admin():
    """Middleware para validar acceso de administrador."""
    if session.get("rol") != "Admin":
        flash("Acceso no autorizado. Se requiere rol de Administrador.", "error")
        return redirect(url_for("dashboard.index"))


def require_login():
    """Middleware para validar que el usuario esté autenticado."""
    if not session.get("ci"):
        flash("Debes iniciar sesión para acceder a esta página.", "error")
        return redirect(url_for("dashboard.index"))


# ------------------------------------------
#ALUMNO
# ------------------------------------------
@auth_bp.route('/login/alumno', methods=['GET'])
def login_alumno_form():
    from modules.forms import LoginAlumnoForm
    
    session.pop('_flashes', None)
    form = LoginAlumnoForm()
    return render_template('login_alumno.html', form=form)

@auth_bp.route('/login/alumno', methods=['POST'])
def login_alumno():
    from modules.forms import LoginAlumnoForm
    
    form = LoginAlumnoForm()
    if not form.validate_on_submit():
        # Flash validation errors
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field}: {error}", "login_error")
        return redirect(url_for('auth_bp.login_alumno_form'))
    
    correo = form.correo.data
    contrasena = form.contrasena.data
    print("== LOGIN ALUMNO ==")
    print("correo:", correo)
    print("pass:", contrasena)

    if not (correo and contrasena):
        flash("Debes ingresar correo y contraseña.", "login_error")
        return redirect(url_for('auth_bp.login_alumno_form'))

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
        session.permanent = True
        flash(f"Bienvenido, {admin['nombre']} (Admin)", "success")
        conexion.cerrar()
        return redirect(url_for("dashboard.dashboard_admin"))
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
        return redirect(url_for('auth_bp.login_alumno_form'))

    # Cargar datos base en session
    session["ci"] = user["ci"]
    session["nombre"] = user["nombre"]
    session.permanent = True
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
        return redirect(url_for("programas.form_participanteprograma"))

    # Tomamos el primer programa (o el que quieras)
    programa = programas[0]
    session["programa"] = programa["nombre_programa"]
    session["tipo_programa"] = programa["tipo"]

    flash(f"Bienvenido, {user['nombre']}", "success")
    return redirect(url_for('dashboard.dashboard_alumno'))


# ------------------------------------------
#DOCENTE
# ------------------------------------------
@auth_bp.route('/login/docente', methods=['GET'])
def login_docente_form():
    from modules.forms import LoginDocenteForm
    
    session.pop('_flashes', None)
    form = LoginDocenteForm()
    return render_template('login_docente.html', form=form)

@auth_bp.route('/login/docente', methods=['POST'])
def login_docente():
    from modules.forms import LoginDocenteForm
    
    form = LoginDocenteForm()
    if not form.validate_on_submit():
        # Flash validation errors
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field}: {error}", "login_error")
        return redirect(url_for('auth_bp.login_docente_form'))
    
    correo = form.correo.data
    contrasena = form.contrasena.data
    print("== LOGIN DOCENTE ==")
    print("correo:", correo)
    print("pass:", contrasena)


    if not (correo and contrasena):
        flash("Debes ingresar correo y contraseña.", "login_error")
        return redirect(url_for('auth_bp.login_docente_form'))

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
        session.permanent = True
        flash(f"Bienvenido, {admin['nombre']} (Admin)", "success")
        conexion.cerrar()
        return redirect(url_for("dashboard.dashboard_admin"))

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
        return redirect(url_for('auth_bp.login_docente_form'))

    # Cargar sesión
    session["ci"] = user["ci"]
    session.permanent = True
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
        return redirect(url_for("programas.form_participanteprograma"))

    programa = programas[0]
    session["programa"] = programa["nombre_programa"]
    session["tipo_programa"] = programa["tipo"]

    flash(f"Bienvenido, {user['nombre']}", "success")
    return redirect(url_for('dashboard.dashboard_docente'))


@auth_bp.route('/logout')
def logout():
    """Cerrar sesión del usuario."""
    nombre = session.get('nombre', 'Usuario')
    session.clear()
    flash(f"Sesión cerrada correctamente. Hasta luego, {nombre}!", "success")
    return redirect(url_for('dashboard.index'))


