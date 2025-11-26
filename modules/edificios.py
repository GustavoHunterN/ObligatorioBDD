from flask import Blueprint, render_template
from Connector import Conexion

edificios_bp = Blueprint('edificios', __name__)


@edificios_bp.route('/edificios/listar', methods=['GET'])
def listar_edificios():
    from modules.auth import require_admin
    unauthorized = require_admin()
    if unauthorized:
        return unauthorized
    conexion = Conexion()
    conexion.cursor.execute("SELECT nombre_edificio, direccion, departamento FROM edificio;")
    edificios = conexion.cursor.fetchall()
    conexion.cerrar()
    return render_template('lista_edificios.html', edificios=edificios)

