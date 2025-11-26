from flask import Blueprint, render_template, session, redirect, url_for, flash
from Connector import Conexion
import control as cont

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
def index():
    session.pop('_flashes', None)
    return render_template('login_index.html')


@dashboard_bp.route('/alumno/home')
def dashboard_alumno():
    from modules.auth import require_role
    unauthorized = require_role("Alumno")

    if unauthorized:
        return unauthorized

    ci = session.get("ci")
    conexion = Conexion()

    # Obtener reservas recientes (últimas 5)
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
        ORDER BY r.fecha DESC, r.id_reserva DESC
        LIMIT 5;
    """, (ci,))
    reservas_recientes = conexion.cursor.fetchall()

    # Contar reservas totales
    conexion.cursor.execute("""
        SELECT COUNT(*) AS total
        FROM reserva_participante
        WHERE ci = %s
    """, (ci,))
    total_reservas = conexion.cursor.fetchone()["total"]

    # Contar reservas activas
    conexion.cursor.execute("""
        SELECT COUNT(*) AS activas
        FROM reserva r
        JOIN reserva_participante rp ON rp.id_reserva = r.id_reserva
        WHERE rp.ci = %s AND r.estado = 'Activa'
    """, (ci,))
    reservas_activas = conexion.cursor.fetchone()["activas"]

    # Obtener programas
    conexion.cursor.execute("""
        SELECT pa.nombre_programa, pr.tipo
        FROM participante_programa pa
        JOIN programa_academico pr ON pr.nombre_programa = pa.nombre_programa
        WHERE pa.ci = %s;
    """, (ci,))
    programas = conexion.cursor.fetchall()

    # Verificar si tiene sanción activa
    tiene_sancion = cont.tiene_sancion_activa(conexion, ci)

    conexion.cerrar()

    return render_template('dashboard_alumno.html',
                         nombre=session.get('nombre'),
                         apellido=session.get('apellido'),
                         reservas_recientes=reservas_recientes,
                         total_reservas=total_reservas,
                         reservas_activas=reservas_activas,
                         programas=programas,
                         tiene_sancion=tiene_sancion)


@dashboard_bp.route('/docente/home')
def dashboard_docente():
    from modules.auth import require_role
    unauthorized = require_role("Docente")
    if unauthorized:
        return unauthorized

    ci = session.get("ci")
    conexion = Conexion()

    # Obtener reservas recientes (últimas 5)
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
        ORDER BY r.fecha DESC, r.id_reserva DESC
        LIMIT 5;
    """, (ci,))
    reservas_recientes = conexion.cursor.fetchall()

    # Contar reservas totales
    conexion.cursor.execute("""
        SELECT COUNT(*) AS total
        FROM reserva_participante
        WHERE ci = %s
    """, (ci,))
    total_reservas = conexion.cursor.fetchone()["total"]

    # Contar reservas activas
    conexion.cursor.execute("""
        SELECT COUNT(*) AS activas
        FROM reserva r
        JOIN reserva_participante rp ON rp.id_reserva = r.id_reserva
        WHERE rp.ci = %s AND r.estado = 'Activa'
    """, (ci,))
    reservas_activas = conexion.cursor.fetchone()["activas"]

    # Reservas pendientes de pasar lista (hoy o pasadas, sin asistencia registrada)
    conexion.cursor.execute("""
        SELECT COUNT(*) AS pendientes
        FROM reserva r
        JOIN reserva_participante rp ON rp.id_reserva = r.id_reserva
        WHERE rp.ci = %s 
          AND r.estado = 'Activa'
          AND r.fecha <= CURDATE()
          AND rp.asistencia IS NULL
    """, (ci,))
    pendientes_lista = conexion.cursor.fetchone()["pendientes"]

    # Obtener programas
    conexion.cursor.execute("""
        SELECT pa.nombre_programa, pr.tipo
        FROM participante_programa pa
        JOIN programa_academico pr ON pr.nombre_programa = pa.nombre_programa
        WHERE pa.ci = %s;
    """, (ci,))
    programas = conexion.cursor.fetchall()

    conexion.cerrar()

    return render_template('dashboard_docente.html',
                         nombre=session.get('nombre'),
                         apellido=session.get('apellido'),
                         reservas_recientes=reservas_recientes,
                         total_reservas=total_reservas,
                         reservas_activas=reservas_activas,
                         pendientes_lista=pendientes_lista,
                         programas=programas)


@dashboard_bp.route('/admin/home')
def dashboard_admin():
    from modules.auth import require_role
    unauthorized = require_role("Admin")
    if unauthorized:
        return unauthorized

    conexion = Conexion()

    # Estadísticas generales
    conexion.cursor.execute("SELECT COUNT(*) AS total FROM participante;")
    total_usuarios = conexion.cursor.fetchone()["total"]

    conexion.cursor.execute("SELECT COUNT(*) AS total FROM reserva;")
    total_reservas = conexion.cursor.fetchone()["total"]

    conexion.cursor.execute("SELECT COUNT(*) AS total FROM reserva WHERE estado = 'Activa';")
    reservas_activas = conexion.cursor.fetchone()["total"]

    conexion.cursor.execute("SELECT COUNT(*) AS total FROM sala;")
    total_salas = conexion.cursor.fetchone()["total"]

    conexion.cursor.execute("SELECT COUNT(*) AS total FROM sancion_participante WHERE fecha_final >= CURDATE();")
    sanciones_activas = conexion.cursor.fetchone()["total"]

    conexion.cursor.execute("SELECT COUNT(*) AS total FROM programa_academico;")
    total_programas = conexion.cursor.fetchone()["total"]

    # Usuarios recientes (últimos 5)
    conexion.cursor.execute("""
        SELECT ci, nombre, apellido, correo, rol
        FROM participante
        ORDER BY ci DESC
        LIMIT 5;
    """)
    usuarios_recientes = conexion.cursor.fetchall()

    # Reservas recientes (últimas 5)
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
        JOIN turnos t ON t.id_turno = r.id_turno
        ORDER BY r.fecha DESC, r.id_reserva DESC
        LIMIT 5;
    """)
    reservas_recientes = conexion.cursor.fetchall()

    conexion.cerrar()

    return render_template('dashboard_admin.html',
                         nombre=session.get('nombre'),
                         apellido=session.get('apellido'),
                         total_usuarios=total_usuarios,
                         total_reservas=total_reservas,
                         reservas_activas=reservas_activas,
                         total_salas=total_salas,
                         sanciones_activas=sanciones_activas,
                         total_programas=total_programas,
                         usuarios_recientes=usuarios_recientes,
                         reservas_recientes=reservas_recientes)
