from flask import Blueprint, render_template, flash, redirect, url_for, session
from Connector import Conexion

bi_bp = Blueprint('bi', __name__)


@bi_bp.route('/bi')
def bi_menu():
    from modules.auth import require_admin
    unauthorized = require_admin()
    if unauthorized:
        return unauthorized

    return render_template("bi/menu.html")


@bi_bp.route('/bi/salas_mas_reservadas')
def bi_salas_mas_reservadas():
    from modules.auth import require_admin
    unauthorized = require_admin()
    if unauthorized:
        return unauthorized
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


@bi_bp.route('/bi/turnos_mas_demandados')
def bi_turnos_mas_demandados():
    from modules.auth import require_admin
    unauthorized = require_admin()
    if unauthorized:
        return unauthorized
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


@bi_bp.route('/bi/promedio_participantes_sala')
def bi_promedio_participantes_sala():
    from modules.auth import require_admin
    unauthorized = require_admin()
    if unauthorized:
        return unauthorized
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


@bi_bp.route('/bi/reservas_por_carrera_facultad')
def bi_reservas_por_carrera_facultad():
    from modules.auth import require_admin
    unauthorized = require_admin()
    if unauthorized:
        return unauthorized
    conexion = Conexion()
    conexion.cursor.execute("""
        SELECT pa.nombre_programa AS programa,
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


@bi_bp.route('/bi/ocupacion_por_edificio')
def bi_ocupacion_por_edificio():
    from modules.auth import require_admin
    unauthorized = require_admin()
    if unauthorized:
        return unauthorized
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


@bi_bp.route('/bi/reservas_asistencias_por_rol')
def bi_reservas_asistencias_por_rol():
    from modules.auth import require_admin
    unauthorized = require_admin()
    if unauthorized:
        return unauthorized
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


@bi_bp.route('/bi/sanciones_por_rol')
def bi_sanciones_por_rol():
    from modules.auth import require_admin
    unauthorized = require_admin()
    if unauthorized:
        return unauthorized
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


@bi_bp.route('/bi/porcentaje_uso')
def bi_porcentaje_uso():
    from modules.auth import require_admin
    unauthorized = require_admin()
    if unauthorized:
        return unauthorized
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


@bi_bp.route('/bi/top_usuarios')
def bi_top_usuarios():
    from modules.auth import require_admin
    unauthorized = require_admin()
    if unauthorized:
        return unauthorized
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


@bi_bp.route('/bi/edificios_por_programa')
def bi_edificios_por_programa():
    from modules.auth import require_admin
    unauthorized = require_admin()
    if unauthorized:
        return unauthorized
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


@bi_bp.route('/bi/capacidad_promedio')
def bi_capacidad_promedio():
    from modules.auth import require_admin
    unauthorized = require_admin()
    if unauthorized:
        return unauthorized
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

