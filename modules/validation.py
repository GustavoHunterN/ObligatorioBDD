"""
Utilidades de validación para datos de formularios.
"""
import re


def sanitize_string(value: str) -> str:
    """
    Sanitiza un string:
    - Elimina espacios al inicio y final
    - Elimina espacios múltiples consecutivos
    - Retorna string vacío si el resultado es None
    """
    if value is None:
        return ""
    if not isinstance(value, str):
        value = str(value)
    # Eliminar espacios al inicio y final
    value = value.strip()
    # Eliminar espacios múltiples consecutivos
    value = re.sub(r'\s+', ' ', value)
    return value


def validate_alphanumeric(value: str, allow_spaces: bool = True, allow_special: list = None):
    """
    Valida que un string contenga solo caracteres alfanuméricos y opcionalmente espacios.
    
    Args:
        value: String a validar
        allow_spaces: Si True, permite espacios dentro del string
        allow_special: Lista de caracteres especiales permitidos (ej: ['-', '_', '.'])
    
    Returns:
        Tuple (is_valid, error_message)
    """
    if not value:
        return True, ""  # Valores vacíos se manejan en otro lugar
    
    sanitized = sanitize_string(value)
    
    # Construir patrón regex
    if allow_spaces:
        pattern = r'^[a-zA-Z0-9\s'
    else:
        pattern = r'^[a-zA-Z0-9'
    
    if allow_special:
        # Escapar caracteres especiales para regex
        escaped = ''.join(re.escape(c) for c in allow_special)
        pattern += escaped
    
    pattern += r']+$'
    
    if not re.match(pattern, sanitized):
        special_chars = f", {', '.join(allow_special)}" if allow_special else ""
        allowed = f"letras, números{', espacios' if allow_spaces else ''}{special_chars}"
        return False, f"El campo solo puede contener {allowed}."
    
    return True, ""


def validate_ci(value: str):
    """
    Valida formato de CI (cédula de identidad).
    Permite solo números, sin espacios ni caracteres especiales.
    """
    if not value:
        return False, "La CI es obligatoria."
    
    sanitized = sanitize_string(value)
    
    # Solo números
    if not re.match(r'^\d+$', sanitized):
        return False, "La CI solo puede contener números."
    
    return True, ""


def validate_and_sanitize_form_data(data: dict, fields_config: dict = None):
    """
    Valida y sanitiza datos de formulario.
    
    Args:
        data: Diccionario con los datos del formulario
        fields_config: Diccionario con configuración de validación por campo.
                      Ejemplo: {
                          'nombre': {'type': 'alphanumeric', 'allow_spaces': True, 'allow_special': ['-']},
                          'ci': {'type': 'ci'},
                          'email': {'type': 'alphanumeric', 'allow_spaces': False, 'allow_special': ['@', '.', '-', '_']}
                      }
    
    Returns:
        Tuple (sanitized_data, errors)
    """
    sanitized = {}
    errors = []
    
    # Configuración por defecto si no se proporciona
    if fields_config is None:
        fields_config = {}
    
    for key, value in data.items():
        # Campos del sistema que no necesitan validación
        if key in ['class_name', 'csrf_token']:
            sanitized[key] = value
            continue
        
        # Si el valor es None o vacío, mantenerlo pero sanitizar
        if value is None:
            sanitized[key] = ""
            continue
        
        # Convertir a string si no lo es
        if not isinstance(value, str):
            value = str(value)
        
        # Obtener configuración del campo
        config = fields_config.get(key, {})
        field_type = config.get('type', 'alphanumeric')
        
        # Sanitizar (siempre)
        sanitized_value = sanitize_string(value)
        sanitized[key] = sanitized_value
        
        # Validar según tipo
        if field_type == 'ci':
            is_valid, error_msg = validate_ci(sanitized_value)
            if not is_valid:
                errors.append(f"{key}: {error_msg}")
        elif field_type == 'alphanumeric':
            allow_spaces = config.get('allow_spaces', True)
            allow_special = config.get('allow_special', [])
            is_valid, error_msg = validate_alphanumeric(sanitized_value, allow_spaces, allow_special)
            if not is_valid:
                errors.append(f"{key}: {error_msg}")
        # Si no hay tipo específico, solo sanitizar (sin validación estricta)
    
    return sanitized, errors

