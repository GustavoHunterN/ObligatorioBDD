import datetime
from flask import (
    Flask, render_template, request, jsonify,
    flash, redirect, url_for, session
)
import control as cont
from Connector import Conexion

app = Flask(__name__)
app.secret_key = "supersecret123"   # Cámbiala si es producción


# =====================================================
# HOME
# =====================================================

@app.route('/')
def index():
    return render_template('base.html')


# =====================================================
#  PROTECCIÓN DE RUTAS
# =====================================================

def require_role(role: str):
    """Middleware simple para validar acceso por rol."""
    if session.get("rol") != role:
        flash("Acceso no autorizado.", "error")
        return redirect(url_for(f'login_{role.lower()}_form'))


# =====================================================
#  LOGIN ALUMNO
# =====================================================

@app.route('/login/alumno', methods=['GET'])
def login_alumno_form():
    session.pop('_flashes', None)
    return render_template('login_alumno.html')


@app.route('/login/alumno', methods=['POST'])
def login_alumno():
    correo = request.form.get('correo')
    contrasena = request.form.get('contrasena')

    if not (correo and contrasena):
        flash("Debes ingresar correo y contraseña.", "login_error")
        return redirect(url_for('login_alumno_form'))

    conexion = Conexion()

    conexion.cursor.execute("""
        SELECT 
            p.ci, 
            p.nombre, 
            p.apellido,
            p.correo
        FROM login l
        JOIN participante p ON p.correo = l.correo
        WHERE l.correo = %s
          AND l.contrasena = %s
          AND RIGHT(p.ci, 1) = 'A'
        LIMIT 1;
    """, (correo, contrasena))

    user = conexion.cursor.fetchone()
    conexion.cerrar()

    if not user:
        flash("Credenciales inválidas para alumno.", "login_error")
        return redirect(url_for('login_alumno_form'))

    session["ci"] = user["ci"]
    session["nombre"] = user["nombre"]
    session["apellido"] = user["apellido"]
    session["correo"] = user["correo"]
    session["rol"] = "Alumno"

    flash(f"Bienvenido, {user['nombre']}", "ok")
    return redirect(url_for('dashboard_alumno'))


@app.route('/alumno/home')
def dashboard_alumno():
    unauthorized = require_role("Alumno")
    if unauthorized:
        return unauthorized
    return f"""<h1>Alumno: {session['nombre']} {session['apellido']}</h1>
            <h2> Sesión iniciada con éxito</h2>"""


# =====================================================
#  LOGIN DOCENTE
# =====================================================

@app.route('/login/docente', methods=['GET'])
def login_docente_form():
    session.pop('_flashes', None)
    return render_template('login_docente.html')


@app.route('/login/docente', methods=['POST'])
def login_docente():
    correo = request.form.get('correo')
    contrasena = request.form.get('contrasena')

    if not (correo and contrasena):
        flash("Debes ingresar correo y contraseña.", "login_error")
        return redirect(url_for('login_docente_form'))

    conexion = Conexion()

    conexion.cursor.execute("""
        SELECT 
            p.ci, 
            p.nombre, 
            p.apellido,
            p.correo
        FROM login l
        JOIN participante p ON p.correo = l.correo
        WHERE l.correo = %s
          AND l.contraseña = %s
          AND RIGHT(p.ci, 1) = 'D'
        LIMIT 1;
    """, (correo, contrasena))

    user = conexion.cursor.fetchone()
    conexion.cerrar()

    if not user:
        flash("Credenciales inválidas para docente.", "login_error")
        return redirect(url_for('login_docente_form'))

    session["ci"] = user["ci"]
    session["nombre"] = user["nombre"]
    session["apellido"] = user["apellido"]
    session["correo"] = user["correo"]
    session["rol"] = "Docente"

    flash(f"Bienvenido, {user['nombre']}", "ok")
    return redirect(url_for('dashboard_docente'))


@app.route('/docente/home')
def dashboard_docente():
    unauthorized = require_role("Docente")
    if unauthorized:
        return unauthorized
    return f"""<h1>Docente: {session['nombre']} {session['apellido']}</h1>
            <h2> Sesión iniciada con éxito</h2>"""


# =====================================================
#  REGISTRAR ALUMNO
# =====================================================

@app.route('/alumnos/nuevo', methods=['GET'])
def form_alumno():
    return render_template('alumnos_form.html')


@app.route('/alumnos/crear', methods=['POST'])
def crear_alumno():
    ci_base = request.form.get('ci')
    nombre = request.form.get('nombre')
    apellido = request.form.get('apellido')
    correo = request.form.get('correo')
    contrasena = request.form.get('contrasena')

    if not (ci_base and nombre and apellido and correo and contrasena):
        flash("Faltan datos para registrar alumno.", "error")
        return redirect(url_for('form_alumno'))

    ci_guardada = ci_base + "A"

    conexion = Conexion()

    conexion.cursor.execute("""
        INSERT INTO login (correo, contrasena)
        VALUES (%s, %s);
    """, (correo, contrasena))

    conexion.cursor.execute("""
        INSERT INTO participante (ci, nombre, apellido, correo)
        VALUES (%s, %s, %s, %s);
    """, (ci_guardada, nombre, apellido, correo))

    conexion.cnx.commit()
    conexion.cerrar()

    flash("Alumno registrado correctamente.", "ok")
    return redirect(url_for('form_alumno'))


# =====================================================
#  REGISTRAR DOCENTE
# =====================================================

@app.route('/docentes/nuevo', methods=['GET'])
def form_docente():
    return render_template('docente_form.html')


@app.route('/docentes/crear', methods=['POST'])
def crear_docente():
    ci_base = request.form.get('ci')
    nombre = request.form.get('nombre')
    apellido = request.form.get('apellido')
    correo = request.form.get('correo')
    contrasena = request.form.get('contrasena')

    if not (ci_base and nombre and apellido and correo and contrasena):
        flash("Faltan datos para registrar docente.", "error")
        return redirect(url_for('form_docente'))

    ci_guardada = ci_base + "D"

    conexion = Conexion()



    try:
        conexion.cursor.execute("""
            INSERT INTO login (correo, contraseña)
            VALUES (%s, %s);
        """, (correo, contrasena))

        conexion.cursor.execute("""
            INSERT INTO participante (ci, nombre, apellido, correo)
            VALUES (%s, %s, %s, %s);
        """, (ci_guardada, nombre, apellido, correo))

        conexion.cnx.commit()
        conexion.cerrar()

        flash("Docente registrado correctamente.", "ok")
        return redirect(url_for('form_docente'))
    except:
        flash('Cuenta ya existente. Intenta Iniciar sesion.', 'error')
        return redirect(url_for('form_docente'))


# =====================================================
#  FORMULARIO EDIFICIO (ya existía)
# =====================================================

@app.route('/FormularioEdificio', methods=['GET'])
def form_Edificio():
    return render_template('edificio_form.html')


# =====================================================
#  OBJECT CREATOR (ya existía)
# =====================================================

@app.route('/ObjectCreator', methods=['POST'])
def object_creator():
    data = request.form
    nombre_clase = data.get('class_name')

    atributos = [valor for clave, valor in data.items() if clave != 'class_name']

    objeto = cont.create_objeto(nombre_clase, atributos)
    if not objeto:
        return jsonify({"error": "Datos inválidos"}), 400

    conexion = Conexion()

    if hasattr(objeto, "save"):
        objeto.save(conexion)
    else:
        conexion.cerrar()
        return jsonify({"error": f"La clase {nombre_clase} no tiene método save()"}), 400

    conexion.cerrar()

    return render_template(
        'success.html',
        mensaje=f"{nombre_clase} creado correctamente",
        clase=nombre_clase,
        datos=objeto.__dict__
    )


# =====================================================
#  🔥 NUEVO: FORM FACULTAD
# =====================================================

@app.route('/FormularioFacultad', methods=['GET'])
def form_Facultad():
    return render_template('facultad_form.html')


# =====================================================
#  🔥 NUEVO: FORM PROGRAMA
# =====================================================

@app.route('/FormularioPrograma', methods=['GET'])
def form_Programa():
    return render_template('programa_form.html')


# =====================================================
#  🔥 NUEVO: LISTAR EDIFICIOS
# =====================================================

@app.route('/edificios/listar', methods=['GET'])
def listar_edificios():
    conexion = Conexion()
    conexion.cursor.execute("SELECT nombre_edificio, direccion, departamento FROM edificio;")
    edificios = conexion.cursor.fetchall()
    conexion.cerrar()
    return render_template('lista_edificios.html', edificios=edificios)


# =====================================================
#  🔥 NUEVO: FORM CREAR RESERVA
# =====================================================

@app.route('/reserva/crear', methods=['GET'])
def reserva_crear():
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

    # Salas con filtro
    if filtro_edificio:
        conexion.cursor.execute("SELECT * FROM sala WHERE edificio=%s;", (filtro_edificio,))
    else:
        conexion.cursor.execute("SELECT * FROM sala;")
    salas = conexion.cursor.fetchall()

    # Reservados por fecha
    reservados = set()
    if fecha:
        conexion.cursor.execute("""
            SELECT id_turno, sala, nombre_edificio
            FROM reserva
            WHERE fecha = %s;
        """, (fecha,))
        reservados = set(
            (r["id_turno"], r["sala"], r["nombre_edificio"])
            for r in conexion.cursor.fetchall()
        )

    conexion.cerrar()

    return render_template(
        "reservas_nueva.html",
        salas=salas,
        turnos=turnos,
        todos_los_turnos=todos_los_turnos,
        edificios=edificios,
        reservados=reservados,
        fecha=fecha,
        filtro_edificio=filtro_edificio,
        filtro_turno=filtro_turno
    )


# =====================================================
#  🔥 NUEVO: GUARDAR RESERVA
# =====================================================

@app.route('/reserva/guardar', methods=['POST'])
def reserva_guardar():
    fecha = request.form.get('fecha')
    # Compatibilidad con distintos nombres de campos del formulario
    sala = request.form.get('sala') or request.form.get('nombre_sala')
    id_turno = request.form.get('id_turno') or request.form.get('turno')
    nombre_edificio = request.form.get('nombre_edificio')

    if not (fecha and sala and id_turno and nombre_edificio):
        flash("Faltan datos para crear la reserva.", "error")
        return redirect(url_for('reserva_crear'))

    # Valor por defecto para el estado de la reserva
    estado = "Activa"

    conexion = Conexion()
    conexion.cursor.execute("""
        INSERT INTO reserva (fecha, estado, id_turno, nombre_edificio, sala)
        VALUES (%s, %s, %s, %s, %s);
    """, (fecha, estado, id_turno, nombre_edificio, sala))
    conexion.cnx.commit()
    conexion.cerrar()

    flash("Reserva creada correctamente.", "ok")
    # Mantenemos la fecha en la URL para que al recargar se vean las reservas de ese día
    return redirect(url_for('reserva_crear', fecha=fecha))


# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":
    app.run(debug=True)