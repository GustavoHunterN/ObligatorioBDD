from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from Connector import Conexion

usuarios_bp = Blueprint('usuarios', __name__)


@usuarios_bp.route('/usuarios', methods=['GET'])
def listar_usuarios():
    from modules.auth import require_admin
    unauthorized = require_admin()
    if unauthorized:
        return unauthorized

    conexion = Conexion()
    conexion.cursor.execute("""
        SELECT ci, nombre, apellido, correo, rol
        FROM participante
        ORDER BY apellido, nombre;
    """)
    usuarios = conexion.cursor.fetchall()
    conexion.cerrar()

    return render_template("usuarios_listado.html", usuarios=usuarios)


@usuarios_bp.route('/usuarios/editar/<ci>', methods=['GET'])
def editar_usuario_form(ci):
    from modules.auth import require_admin
    from modules.security import validate_ci
    from modules.forms import UsuarioEditForm
    
    unauthorized = require_admin()
    if unauthorized:
        return unauthorized
    
    # Validate CI parameter
    ci = validate_ci(ci)

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
        return redirect(url_for("usuarios.listar_usuarios"))

    # Populate form with existing data
    form = UsuarioEditForm()
    form.nombre.data = usuario['nombre']
    form.apellido.data = usuario['apellido']
    form.correo.data = usuario['correo']
    form.rol.data = usuario['rol']

    return render_template("usuario_editar.html", usuario=usuario, form=form)


@usuarios_bp.route('/usuarios/editar/<ci>', methods=['POST'])
def editar_usuario(ci):
    from modules.auth import require_admin
    from modules.security import validate_ci
    from modules.forms import UsuarioEditForm
    
    unauthorized = require_admin()
    if unauthorized:
        return unauthorized
    
    # Validate CI parameter
    ci = validate_ci(ci)

    form = UsuarioEditForm()
    if not form.validate_on_submit():
        # Flash validation errors
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field}: {error}", "error")
        return redirect(url_for("usuarios.editar_usuario_form", ci=ci))

    conexion = Conexion()
    conexion.cursor.execute("""
        UPDATE participante
        SET nombre = %s, apellido = %s, correo = %s, rol = %s
        WHERE ci = %s;
    """, (form.nombre.data, form.apellido.data, form.correo.data, form.rol.data, ci))

    conexion.cnx.commit()
    conexion.cerrar()

    flash("Usuario actualizado correctamente.", "success")
    return redirect(url_for("usuarios.listar_usuarios"))


@usuarios_bp.route('/usuarios/eliminar/<ci>', methods=['POST'])
def eliminar_usuario(ci):
    from modules.auth import require_admin
    from modules.security import validate_ci
    
    unauthorized = require_admin()
    if unauthorized:
        return unauthorized
    
    # Validate CI parameter
    ci = validate_ci(ci)

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

    flash("Usuario eliminado correctamente.", "success")
    return redirect(url_for("usuarios.listar_usuarios"))


@usuarios_bp.route('/usuarios/<ci>/programas', methods=['GET'])
def programas_de_usuario(ci):
    from modules.auth import require_admin
    from modules.security import validate_ci
    
    unauthorized = require_admin()
    if unauthorized:
        return unauthorized
    
    # Validate CI parameter
    ci = validate_ci(ci)

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


@usuarios_bp.route('/usuarios/<ci>/programas/eliminar', methods=['POST'])
def eliminar_usuario_de_programa(ci):
    from modules.auth import require_admin
    from modules.security import validate_ci, validate_programa_name
    
    unauthorized = require_admin()
    if unauthorized:
        return unauthorized
    
    # Validate CI parameter
    ci = validate_ci(ci)
    
    # Validate programa parameter
    from modules.forms import EliminarProgramaForm
    
    form = EliminarProgramaForm()
    if not form.validate_on_submit():
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field}: {error}", "error")
        return redirect(url_for("usuarios.programas_de_usuario", ci=ci))
    
    programa = form.programa.data

    conexion = Conexion()
    conexion.cursor.execute("""
        DELETE FROM participante_programa
        WHERE ci = %s AND nombre_programa = %s;
    """, (ci, programa))
    conexion.cnx.commit()
    conexion.cerrar()

    flash(f"El usuario fue dado de baja del programa {programa}.", "success")
    return redirect(url_for("usuarios.programas_de_usuario", ci=ci))

