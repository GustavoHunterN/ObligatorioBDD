from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from mysql.connector.errors import IntegrityError
import control as cont
from Connector import Conexion

formularios_bp = Blueprint('formularios', __name__)


@formularios_bp.route('/alumnos/nuevo', methods=['GET'])
def form_alumno():
    from modules.auth import require_admin
    from modules.forms import AlumnoForm
    
    unauthorized = require_admin()
    if unauthorized:
        return unauthorized
    
    form = AlumnoForm()
    return render_template('alumno_form.html', form=form)


@formularios_bp.route('/docentes/nuevo', methods=['GET'])
def form_docente():
    from modules.auth import require_admin
    from modules.forms import DocenteForm
    
    unauthorized = require_admin()
    if unauthorized:
        return unauthorized
    
    form = DocenteForm()
    return render_template('docente_form.html', form=form)


@formularios_bp.route('/FormularioEdificio', methods=['GET'])
def form_edificio():
    from modules.auth import require_admin
    from modules.forms import EdificioForm
    
    unauthorized = require_admin()
    if unauthorized:
        return unauthorized
    
    form = EdificioForm()
    return render_template('edificio_form.html', form=form)


@formularios_bp.route('/FormularioSala', methods=['GET'])
def form_sala():
    from modules.auth import require_admin
    from modules.forms import SalaForm
    
    unauthorized = require_admin()
    if unauthorized:
        return unauthorized
    
    conexion = Conexion()
    conexion.cursor.execute("SELECT nombre_edificio FROM edificio")
    edificios = conexion.cursor.fetchall()
    conexion.cerrar()

    form = SalaForm()
    # Populate edificio choices
    form.edificio.choices = [(e['nombre_edificio'], e['nombre_edificio']) for e in edificios]
    
    return render_template("sala_form.html", form=form, edificios=edificios)


@formularios_bp.route('/FormularioFacultad', methods=['GET'])
def form_facultad():
    from modules.auth import require_admin
    from modules.forms import FacultadForm
    
    unauthorized = require_admin()
    if unauthorized:
        return unauthorized
    
    form = FacultadForm()
    return render_template('facultad_form.html', form=form)


@formularios_bp.route('/FormularioPrograma')
def form_programa():
    from modules.auth import require_admin
    from modules.forms import ProgramaForm
    
    unauthorized = require_admin()
    if unauthorized:
        return unauthorized
    
    conexion = Conexion()
    conexion.cursor.execute("SELECT nombre FROM facultad;")
    facultades = conexion.cursor.fetchall()
    conexion.cerrar()

    form = ProgramaForm()
    # Populate facultad choices
    form.nombre_facultad.choices = [(f['nombre'], f['nombre']) for f in facultades]
    
    return render_template("programa_form.html", form=form, facultades=facultades)


@formularios_bp.route('/ObjectCreator', methods=['POST'])
def object_creator():
    from modules.auth import require_login
    from modules.forms import AlumnoForm, DocenteForm, EdificioForm, FacultadForm, SalaForm, ProgramaForm, ParticipanteProgramaForm
    from modules.security import validate_class_name
    
    unauthorized = require_login()
    if unauthorized:
        return unauthorized
    
    # Get class_name to determine which form to use
    nombre_clase = request.form.get('class_name', '')
    nombre_clase = validate_class_name(nombre_clase)
    
    # Reserva no usa formulario Flask-WTF, se procesa directamente
    if nombre_clase == "Reserva":
        # Validar CSRF token manualmente para Reserva
        from flask_wtf.csrf import validate_csrf
        try:
            validate_csrf(request.form.get('csrf_token'))
        except Exception as e:
            flash("Error de seguridad. Por favor, intenta nuevamente.", "error")
            return redirect(url_for('reservas.form_reserva'))
        
        # Continuar con el procesamiento de Reserva (salta validación de formulario)
        conexion = Conexion()
        raw_data = {}
        for key in request.form:
            if key != 'csrf_token':
                raw_data[key] = request.form.get(key)
        
        # Obtener edificio desde sala
        edificio = cont.get_edificio_from_sala(conexion, raw_data.get("sala"))
        if not edificio:
            conexion.cerrar()
            flash("No se pudo obtener el edificio de la sala seleccionada.", "error")
            return redirect(url_for("reservas.form_reserva"))

        # insertarlo en data ANTES de ordenar args
        raw_data["edificio"] = edificio
        
        # ⭐ VALIDAR RESTRICCIONES AQUÍ ⭐
        ok, msg = cont.restriccion_reserva(
            conexion,
            raw_data.get("ci_sesion"),
            raw_data.get("fecha"),
            raw_data.get("sala"),
            session.get("rol"),
            session.get("tipo_programa")
        )
        if not ok:
            conexion.cerrar()
            flash(msg, "error")
            return redirect(url_for("reservas.form_reserva"))
        
        # ahora sí: usar ordenar_args
        args = cont.ordenar_args(nombre_clase, raw_data)
        
        # Crear el objeto con args correctos
        objeto = cont.create_objeto(nombre_clase, args)
        try:
            objeto.save(conexion)
        except ValueError as e:
            conexion.cerrar()
            flash(str(e), "error")
            return redirect(url_for("reservas.form_reserva"))
        
        raw_data["id_reserva"] = str(objeto.id_reserva)
        raw_data["participante"] = raw_data.get("ci_sesion")
        rpargs = cont.ordenar_args("ReservaParticipante", raw_data)
        rp = cont.create_objeto("ReservaParticipante", rpargs)
        try:
            rp.save(conexion)
        except ValueError as e:
            conexion.cerrar()
            flash(str(e), "error")
            return redirect(url_for("reservas.form_reserva"))

        # Obtener lista de participantes (alumno o docente)
        lista_cis = cont.Reserva_Lista_participantes(raw_data, request)

        for ci_part in lista_cis:
            data_rp = {
                "id_reserva": str(objeto.id_reserva),
                "participante": ci_part
            }
            rpargs = cont.ordenar_args("ReservaParticipante", data_rp)
            rp = cont.create_objeto("ReservaParticipante", rpargs)
            try:
                rp.save(conexion)
            except ValueError as e:
                conexion.cerrar()
                flash(str(e), "error")
                return redirect(url_for("reservas.form_reserva"))
        
        # Limpiar programa_reserva de la sesión después de crear la reserva
        session.pop("programa_reserva", None)
        session.pop("tipo_programa", None)
        conexion.cerrar()
        flash("Reserva creada correctamente.", "success")
        return redirect(url_for("reservas.mis_reservas"))
    
    # Para otros tipos, usar formularios Flask-WTF
    # Instantiate appropriate form based on class_name
    form_map = {
        'Alumno': AlumnoForm,
        'Docente': DocenteForm,
        'Edificio': EdificioForm,
        'Facultad': FacultadForm,
        'Sala': SalaForm,
        'Programa': ProgramaForm,
        'ParticipantePrograma': ParticipanteProgramaForm,
    }
    
    FormClass = form_map.get(nombre_clase)
    if not FormClass:
        flash("Tipo de formulario no válido.", "error")
        return redirect(url_for('dashboard.index'))
    
    form = FormClass()
    
    # Populate dynamic choices if needed
    if nombre_clase == 'Sala':
        conexion_temp = Conexion()
        conexion_temp.cursor.execute("SELECT nombre_edificio FROM edificio")
        edificios = conexion_temp.cursor.fetchall()
        conexion_temp.cerrar()
        form.edificio.choices = [(e['nombre_edificio'], e['nombre_edificio']) for e in edificios]
    elif nombre_clase == 'Programa':
        conexion_temp = Conexion()
        conexion_temp.cursor.execute("SELECT nombre FROM facultad;")
        facultades = conexion_temp.cursor.fetchall()
        conexion_temp.cerrar()
        form.nombre_facultad.choices = [(f['nombre'], f['nombre']) for f in facultades]
    
    # Validate form
    if not form.validate_on_submit():
        # Flash validation errors
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field}: {error}", "error")
        
        # Redirect to appropriate form
        route_map = {
            'Alumno': 'formularios.form_alumno',
            'Docente': 'formularios.form_docente',
            'Edificio': 'formularios.form_edificio',
            'Sala': 'formularios.form_sala',
            'Facultad': 'formularios.form_facultad',
            'Programa': 'formularios.form_programa',
            'ParticipantePrograma': 'programas.form_participanteprograma',
        }
        redirect_route = route_map.get(nombre_clase, 'dashboard.index')
        return redirect(url_for(redirect_route))
    
    # Convert form data to dict (using .data for all fields)
    raw_data = {}
    for field in form:
        if field.name != 'csrf_token':
            raw_data[field.name] = field.data
    
    # Configuración de validación por tipo de objeto
    validation_configs = {
        'Alumno': {
            'ci': {'type': 'ci'},
            'nombre': {'type': 'alphanumeric', 'allow_spaces': True, 'allow_special': []},
            'apellido': {'type': 'alphanumeric', 'allow_spaces': True, 'allow_special': []},
        },
        'Docente': {
            'ci': {'type': 'ci'},
            'nombre': {'type': 'alphanumeric', 'allow_spaces': True, 'allow_special': []},
            'apellido': {'type': 'alphanumeric', 'allow_spaces': True, 'allow_special': []},
        },
        'Facultad': {
            'nombre': {'type': 'alphanumeric', 'allow_spaces': True, 'allow_special': ['-']},
        },
        'Edificio': {
            'nombre_edificio': {'type': 'alphanumeric', 'allow_spaces': False, 'allow_special': []},
        },
        'Programa': {
            'nombre_programa': {'type': 'alphanumeric', 'allow_spaces': True, 'allow_special': ['-', '_']},
        },
        'Sala': {
            'nombre_sala': {'type': 'alphanumeric', 'allow_spaces': False, 'allow_special': []},
        },
    }
    
    from modules.security import validate_class_name
    from modules.validation import validate_and_sanitize_form_data
    
    nombre_clase = raw_data.get('class_name', '')
    # Validate class_name against whitelist
    nombre_clase = validate_class_name(nombre_clase)
    validation_config = validation_configs.get(nombre_clase, {})
    
    data, validation_errors = validate_and_sanitize_form_data(raw_data, validation_config)
    
    if validation_errors:
        conexion = Conexion()
        conexion.cerrar()
        for error in validation_errors:
            flash(error, "error")
        # Redirigir al formulario correspondiente
        route_map = {
            'alumno': 'formularios.form_alumno',
            'docente': 'formularios.form_docente',
            'edificio': 'formularios.form_edificio',
            'sala': 'formularios.form_sala',
            'facultad': 'formularios.form_facultad',
            'programa': 'formularios.form_programa',
        }
        redirect_route = route_map.get(nombre_clase.lower(), 'dashboard.index')
        return redirect(url_for(redirect_route))
    
    print("DATA COMPLETO (sanitizado):", data)
    conexion = Conexion()
    
    # Mapeo de nombres de clase a rutas de blueprint
    route_map = {
        'alumno': 'formularios.form_alumno',
        'docente': 'formularios.form_docente',
        'edificio': 'formularios.form_edificio',
        'sala': 'formularios.form_sala',
        'facultad': 'formularios.form_facultad',
        'programa': 'formularios.form_programa',
        'reserva': 'reservas.form_reserva',
        'participanteprograma': 'programas.form_participanteprograma'
    }
    object_temp = route_map.get(nombre_clase.lower(), 'dashboard.index')

    # Nota: El manejo de "Reserva" se hace al inicio del método, antes de validar formularios Flask-WTF

    if nombre_clase == "Sala" and "cantidad" in data:
        cantidad = int(data["cantidad"])
        capacidad = int(data["capacidad"])
        tipo = data["tipo"]
        edificio = data["edificio"]
        data.pop("cantidad")
        conexion = Conexion()
        salas_creadas = 0
        salas_duplicadas = []
        for i in range(1, cantidad + 1):
            nombre_sala = f"{edificio[0].upper()}{i:03d}"
            obj = cont.create_objeto("Sala", [nombre_sala, capacidad, tipo, edificio])
            try:
                obj.save(conexion)
                salas_creadas += 1
            except ValueError as e:
                salas_duplicadas.append(nombre_sala)
        conexion.cerrar()
        if salas_duplicadas:
            flash(f"Se crearon {salas_creadas} salas. Las siguientes ya existían: {', '.join(salas_duplicadas)}", "warning")
        else:
            flash(f"{salas_creadas} salas generadas correctamente", "success")
        return redirect(url_for('formularios.form_sala'))

    else:
        args = cont.ordenar_args(nombre_clase, data)
        objeto = cont.create_objeto(nombre_clase, args)
        try:
            objeto.save(conexion)
        except ValueError as e:
            # Catch duplicate/existence errors from save() methods
            conexion.cerrar()
            session.pop('_flashes', None)
            flash(str(e), "error")
            return redirect(url_for(object_temp))
        except IntegrityError:
            conexion.cerrar()
            session.pop('_flashes', None)
            flash("El objeto ya existe o viola una restricción única.", "error")
            return redirect(url_for(object_temp))
        except Exception as e:
            conexion.cerrar()
            session.pop('_flashes', None)
            flash(f"Error inesperado: {str(e)}", "error")
            return redirect(url_for('dashboard.index'))

    conexion.cerrar()
    session.pop('_flashes', None)
    print(f"{nombre_clase} creado correctamente.", "ok")
    flash(f"{nombre_clase} creado correctamente.", "success")
    return redirect(url_for(object_temp))

