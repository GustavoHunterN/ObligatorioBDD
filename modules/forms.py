"""
Flask-WTF Form classes for all application forms.
"""
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, EmailField, PasswordField, DateField, HiddenField
from wtforms.validators import DataRequired, Length, Email, Regexp, NumberRange, Optional
from wtforms.widgets import TextArea


class AlumnoForm(FlaskForm):
    """Form for creating a new Alumno."""
    class_name = HiddenField(default="Alumno")
    ci = StringField('CI', validators=[
        DataRequired(message="La CI es obligatoria."),
        Length(min=1, max=9, message="La CI debe tener entre 1 y 9 caracteres."),
        Regexp(r'^[A-Za-z0-9]+$', message="La CI solo puede contener letras y números.")
    ])
    nombre = StringField('Nombre', validators=[
        DataRequired(message="El nombre es obligatorio."),
        Length(min=1, max=15, message="El nombre debe tener entre 1 y 15 caracteres."),
        Regexp(r'^[A-Za-z\s]+$', message="El nombre solo puede contener letras y espacios.")
    ])
    apellido = StringField('Apellido', validators=[
        DataRequired(message="El apellido es obligatorio."),
        Length(min=1, max=15, message="El apellido debe tener entre 1 y 15 caracteres."),
        Regexp(r'^[A-Za-z\s]+$', message="El apellido solo puede contener letras y espacios.")
    ])
    contrasena = PasswordField('Contraseña', validators=[
        DataRequired(message="La contraseña es obligatoria."),
        Length(min=1, max=64, message="La contraseña debe tener entre 1 y 64 caracteres.")
    ])


class DocenteForm(FlaskForm):
    """Form for creating a new Docente (Participante)."""
    class_name = HiddenField(default="Docente")
    type = HiddenField(default="docente")
    ci = StringField('CI (sin letra)', validators=[
        DataRequired(message="La CI es obligatoria."),
        Length(min=1, max=8, message="La CI debe tener entre 1 y 8 caracteres."),
        Regexp(r'^[0-9]+$', message="La CI solo puede contener números.")
    ])
    nombre = StringField('Nombre', validators=[
        DataRequired(message="El nombre es obligatorio."),
        Length(min=1, max=15, message="El nombre debe tener entre 1 y 15 caracteres."),
        Regexp(r'^[A-Za-z\s]+$', message="El nombre solo puede contener letras y espacios.")
    ])
    apellido = StringField('Apellido', validators=[
        DataRequired(message="El apellido es obligatorio."),
        Length(min=1, max=15, message="El apellido debe tener entre 1 y 15 caracteres."),
        Regexp(r'^[A-Za-z\s]+$', message="El apellido solo puede contener letras y espacios.")
    ])
    contrasena = PasswordField('Contraseña', validators=[
        DataRequired(message="La contraseña es obligatoria."),
        Length(min=1, max=64, message="La contraseña debe tener entre 1 y 64 caracteres.")
    ])


class EdificioForm(FlaskForm):
    """Form for creating a new Edificio."""
    class_name = HiddenField(default="Edificio")
    nombre = StringField('Nombre', validators=[
        DataRequired(message="El nombre es obligatorio."),
        Length(min=1, max=15, message="El nombre debe tener entre 1 y 15 caracteres."),
        Regexp(r'^[A-Za-z0-9]+$', message="El nombre solo puede contener letras y números.")
    ])
    direccion = StringField('Dirección', validators=[
        DataRequired(message="La dirección es obligatoria."),
        Length(min=1, max=30, message="La dirección debe tener entre 1 y 30 caracteres.")
    ])
    departamento = StringField('Departamento', validators=[
        DataRequired(message="El departamento es obligatorio."),
        Length(min=1, max=10, message="El departamento debe tener entre 1 y 10 caracteres.")
    ])


class FacultadForm(FlaskForm):
    """Form for creating a new Facultad."""
    class_name = HiddenField(default="Facultad")
    Nombre = StringField('Nombre', validators=[
        DataRequired(message="El nombre es obligatorio."),
        Length(min=1, max=15, message="El nombre debe tener entre 1 y 15 caracteres."),
        Regexp(r'^[A-Za-z0-9\s\-]+$', message="El nombre solo puede contener letras, números, espacios e hyphens.")
    ])


class SalaForm(FlaskForm):
    """Form for creating multiple Salas."""
    class_name = HiddenField(default="Sala")
    edificio = SelectField('Edificio', validators=[
        DataRequired(message="El edificio es obligatorio.")
    ], choices=[])  # Choices will be populated dynamically
    cantidad = IntegerField('Cantidad de salas a crear', validators=[
        DataRequired(message="La cantidad es obligatoria."),
        NumberRange(min=1, max=100, message="La cantidad debe estar entre 1 y 100.")
    ])
    capacidad = IntegerField('Capacidad por sala', validators=[
        DataRequired(message="La capacidad es obligatoria."),
        NumberRange(min=1, max=1000, message="La capacidad debe estar entre 1 y 1000.")
    ])
    tipo = SelectField('Tipo de sala', validators=[
        DataRequired(message="El tipo es obligatorio.")
    ], choices=[
        ('Libre', 'Libre'),
        ('Docente', 'Docente'),
        ('Posgrado', 'Posgrado')
    ])


class ProgramaForm(FlaskForm):
    """Form for creating a new Programa."""
    class_name = HiddenField(default="Programa")
    nombre = StringField('Nombre', validators=[
        DataRequired(message="El nombre es obligatorio."),
        Length(min=1, max=30, message="El nombre debe tener entre 1 y 30 caracteres."),
        Regexp(r'^[A-Za-z0-9\s\-_]+$', message="El nombre solo puede contener letras, números, espacios, hyphens y underscores.")
    ])
    nombre_facultad = SelectField('Facultad', validators=[
        DataRequired(message="La facultad es obligatoria.")
    ], choices=[])  # Choices will be populated dynamically
    tipo = SelectField('Tipo', validators=[
        DataRequired(message="El tipo es obligatorio.")
    ], choices=[
        ('Grado', 'Grado'),
        ('Posgrado', 'Posgrado')
    ])


class ParticipanteProgramaForm(FlaskForm):
    """Form for enrolling in a Programa (hidden fields)."""
    class_name = HiddenField(default="ParticipantePrograma")
    programa = HiddenField(validators=[DataRequired()])
    participante = HiddenField(validators=[DataRequired()])
    rol = HiddenField(validators=[DataRequired()])


class LoginAlumnoForm(FlaskForm):
    """Form for Alumno login."""
    correo = EmailField('Correo', validators=[
        DataRequired(message="El correo es obligatorio."),
        Email(message="Debe ser un correo electrónico válido.")
    ])
    contrasena = PasswordField('Contraseña', validators=[
        DataRequired(message="La contraseña es obligatoria.")
    ])


class LoginDocenteForm(FlaskForm):
    """Form for Docente login."""
    correo = EmailField('Correo', validators=[
        DataRequired(message="El correo es obligatorio."),
        Email(message="Debe ser un correo electrónico válido.")
    ])
    contrasena = PasswordField('Contraseña', validators=[
        DataRequired(message="La contraseña es obligatoria.")
    ])


class UsuarioEditForm(FlaskForm):
    """Form for editing a Usuario."""
    nombre = StringField('Nombre', validators=[
        DataRequired(message="El nombre es obligatorio."),
        Length(min=1, max=15, message="El nombre debe tener entre 1 y 15 caracteres."),
        Regexp(r'^[A-Za-z\s]+$', message="El nombre solo puede contener letras y espacios.")
    ])
    apellido = StringField('Apellido', validators=[
        DataRequired(message="El apellido es obligatorio."),
        Length(min=1, max=15, message="El apellido debe tener entre 1 y 15 caracteres."),
        Regexp(r'^[A-Za-z\s]+$', message="El apellido solo puede contener letras y espacios.")
    ])
    correo = EmailField('Correo', validators=[
        DataRequired(message="El correo es obligatorio."),
        Email(message="Debe ser un correo electrónico válido."),
        Length(max=30, message="El correo no puede exceder 30 caracteres.")
    ])
    rol = SelectField('Rol', validators=[
        DataRequired(message="El rol es obligatorio.")
    ], choices=[
        ('Alumno', 'Alumno'),
        ('Docente', 'Docente'),
        ('Admin', 'Admin')
    ])


class SalaEditForm(FlaskForm):
    """Form for editing a Sala."""
    capacidad = IntegerField('Capacidad', validators=[
        DataRequired(message="La capacidad es obligatoria."),
        NumberRange(min=1, max=1000, message="La capacidad debe estar entre 1 y 1000.")
    ])
    tipo = SelectField('Tipo', validators=[
        DataRequired(message="El tipo es obligatorio.")
    ], choices=[
        ('Libre', 'Libre'),
        ('Docente', 'Docente'),
        ('Posgrado', 'Posgrado')
    ])
    edificio = SelectField('Edificio', validators=[
        DataRequired(message="El edificio es obligatorio.")
    ], choices=[])  # Choices will be populated dynamically


class ReservaEditForm(FlaskForm):
    """Form for editing a Reserva."""
    fecha = DateField('Fecha', validators=[
        DataRequired(message="La fecha es obligatoria.")
    ], format='%Y-%m-%d')
    sala = SelectField('Sala', validators=[
        DataRequired(message="La sala es obligatoria.")
    ], choices=[])  # Choices will be populated dynamically
    id_turno = SelectField('Turno', validators=[
        DataRequired(message="El turno es obligatorio.")
    ], choices=[])  # Choices will be populated dynamically
    nombre_edificio = SelectField('Edificio', validators=[
        DataRequired(message="El edificio es obligatorio.")
    ], choices=[])  # Choices will be populated dynamically
    estado = SelectField('Estado', validators=[
        DataRequired(message="El estado es obligatorio.")
    ], choices=[
        ('Activa', 'Activa'),
        ('Cancelada', 'Cancelada'),
        ('S/A', 'S/A'),
        ('Finalizada', 'Finalizada')
    ])


class SancionEditForm(FlaskForm):
    """Form for editing a Sancion."""
    fecha_final = DateField('Fecha Final', validators=[
        DataRequired(message="La fecha final es obligatoria.")
    ], format='%Y-%m-%d')


class EliminarProgramaForm(FlaskForm):
    """Form for removing a user from a programa."""
    programa = StringField('Programa', validators=[
        DataRequired(message="El programa es obligatorio."),
        Length(min=1, max=30, message="El nombre del programa debe tener entre 1 y 30 caracteres."),
        Regexp(r'^[A-Za-z0-9\s\-_]+$', message="El nombre del programa tiene formato inválido.")
    ])

