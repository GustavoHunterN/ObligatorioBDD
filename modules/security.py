"""
Utilidades de validación de seguridad para rutas Flask.
"""
from flask import abort
import re


def validate_ci(ci: str) -> str:
    """
    Valida formato de CI: alfanumérico, máximo 9 caracteres.
    Retorna CI sanitizado o lanza abort(400).
    """
    if not ci or not isinstance(ci, str):
        abort(400, "CI inválida: debe ser una cadena de texto.")
    
    ci = ci.strip()
    
    # Formato CI: alfanumérico, máximo 9 caracteres
    if not re.match(r'^[A-Za-z0-9]{1,9}$', ci):
        abort(400, f"CI inválida: formato incorrecto. Recibido: {ci}")
    
    return ci


def validate_int_param(value, param_name: str, min_val: int = None, max_val: int = None) -> int:
    """
    Valida parámetro entero de URL.
    Retorna int o lanza abort(400).
    """
    if value is None:
        abort(400, f"Parámetro '{param_name}' es requerido.")
    
    try:
        int_val = int(value)
    except (ValueError, TypeError):
        abort(400, f"Parámetro '{param_name}' debe ser un número entero. Recibido: {value}")
    
    if min_val is not None and int_val < min_val:
        abort(400, f"Parámetro '{param_name}' debe ser >= {min_val}. Recibido: {int_val}")
    
    if max_val is not None and int_val > max_val:
        abort(400, f"Parámetro '{param_name}' debe ser <= {max_val}. Recibido: {int_val}")
    
    return int_val


def validate_str_param(value, param_name: str, max_length: int = None, 
                      pattern: str = None, allow_empty: bool = False) -> str:
    """
    Valida parámetro string de URL.
    Retorna string sanitizado o lanza abort(400).
    """
    if value is None:
        if allow_empty:
            return ""
        abort(400, f"Parámetro '{param_name}' es requerido.")
    
    if not isinstance(value, str):
        value = str(value)
    
    value = value.strip()
    
    if not allow_empty and not value:
        abort(400, f"Parámetro '{param_name}' no puede estar vacío.")
    
    if max_length and len(value) > max_length:
        abort(400, f"Parámetro '{param_name}' excede la longitud máxima de {max_length} caracteres.")
    
    if pattern and not re.match(pattern, value):
        abort(400, f"Parámetro '{param_name}' tiene formato inválido. Recibido: {value}")
    
    return value


def validate_sala_name(nombre_sala: str) -> str:
    """
    Valida formato de nombre de sala: alfanumérico, máximo 5 caracteres.
    """
    return validate_str_param(nombre_sala, "nombre_sala", max_length=5, 
                             pattern=r'^[A-Za-z0-9]{1,5}$')


def validate_programa_name(programa: str) -> str:
    """
    Valida formato de nombre de programa: alfanumérico, espacios, guiones, guiones bajos, máximo 30 caracteres.
    """
    return validate_str_param(programa, "programa", max_length=30,
                             pattern=r'^[A-Za-z0-9\s\-_]{1,30}$')


def validate_edificio_name(edificio: str) -> str:
    """
    Valida formato de nombre de edificio: alfanumérico, máximo 15 caracteres.
    """
    return validate_str_param(edificio, "edificio", max_length=15,
                             pattern=r'^[A-Za-z0-9]{1,15}$')


def validate_rol(rol: str) -> str:
    """
    Valida rol: debe ser uno de los valores permitidos.
    """
    allowed_roles = ['Admin', 'Alumno', 'Docente']
    if rol not in allowed_roles:
        abort(400, f"Rol inválido: debe ser uno de {allowed_roles}. Recibido: {rol}")
    return rol


def validate_date_string(date_str: str, param_name: str = "fecha") -> str:
    """
    Valida formato de fecha string: YYYY-MM-DD.
    """
    if not date_str:
        abort(400, f"Parámetro '{param_name}' es requerido.")
    
    if not re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
        abort(400, f"Parámetro '{param_name}' debe tener formato YYYY-MM-DD. Recibido: {date_str}")
    
    return date_str


def validate_class_name(class_name: str) -> str:
    """
    Valida class_name en ObjectCreator: debe estar en la lista blanca.
    """
    allowed_classes = ['Alumno', 'Docente', 'Edificio', 'Sala', 'Facultad', 
                       'Programa', 'Reserva', 'ReservaParticipante', 'ParticipantePrograma']
    
    if class_name not in allowed_classes:
        abort(400, f"Nombre de clase inválido: '{class_name}'. Permitidos: {allowed_classes}")
    
    return class_name

