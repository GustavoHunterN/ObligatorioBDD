from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import control as cont
from Connector import Conexion

sanciones_bp = Blueprint('sanciones', __name__)


@sanciones_bp.route('/sanciones', methods=['GET'])
def listar_sanciones():
    # Solo docentes (o BI) pueden editar sanciones
   # if session.get("rol") != "Admin":
    #    flash("Acceso no autorizado.", "error")
     #   return redirect(url_for("dashboard.index"))

    conexion = Conexion()
    sanciones = cont.obtener_sanciones(conexion)
    conexion.cerrar()

    return render_template("sanciones_listado.html", sanciones=sanciones)


@sanciones_bp.route('/sanciones/editar/<int:id_sancion>', methods=['GET'])
def editar_sancion_form(id_sancion):
    from modules.auth import require_admin
    from modules.security import validate_int_param
    
    unauthorized = require_admin()
    if unauthorized:
        return unauthorized
    
    # Validate id_sancion parameter
    id_sancion = validate_int_param(id_sancion, "id_sancion", min_val=1)

    conexion = Conexion()
    sancion = cont.obtener_sancion_por_id(conexion, id_sancion)
    conexion.cerrar()

    if not sancion:
        flash("Sanción no encontrada.", "error")
        return redirect(url_for("sanciones.listar_sanciones"))
    
    # Populate form with existing data
    from modules.forms import SancionEditForm
    from datetime import datetime
    form = SancionEditForm()
    if sancion['fecha_final']:
        form.fecha_final.data = sancion['fecha_final']

    return render_template("sancion_editar.html", sancion=sancion, form=form)


@sanciones_bp.route('/sanciones/editar/<int:id_sancion>', methods=['POST'])
def editar_sancion(id_sancion):
    from modules.auth import require_admin
    from modules.security import validate_int_param
    from modules.forms import SancionEditForm
    
    unauthorized = require_admin()
    if unauthorized:
        return unauthorized
    
    # Validate id_sancion parameter
    id_sancion = validate_int_param(id_sancion, "id_sancion", min_val=1)

    form = SancionEditForm()
    if not form.validate_on_submit():
        # Flash validation errors
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field}: {error}", "error")
        return redirect(url_for("sanciones.editar_sancion_form", id_sancion=id_sancion))
    
    fecha_final = form.fecha_final.data.strftime('%Y-%m-%d')

    conexion = Conexion()
    cont.actualizar_sancion(conexion, id_sancion, fecha_final)
    conexion.cnx.commit()
    conexion.cerrar()

    flash("Sanción actualizada correctamente.", "success")
    return redirect(url_for("sanciones.listar_sanciones"))


@sanciones_bp.route('/sanciones/eliminar/<int:id_sancion>', methods=['POST'])
def eliminar_sancion(id_sancion):
    from modules.auth import require_admin
    from modules.security import validate_int_param
    
    unauthorized = require_admin()
    if unauthorized:
        return unauthorized
    
    # Validate id_sancion parameter
    id_sancion = validate_int_param(id_sancion, "id_sancion", min_val=1)

    conexion = Conexion()
    cont.eliminar_sancion(conexion, id_sancion)
    conexion.cnx.commit()
    conexion.cerrar()

    flash("Sanción eliminada correctamente.", "success")
    return redirect(url_for("sanciones.listar_sanciones"))

