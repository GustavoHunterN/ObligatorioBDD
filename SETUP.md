# Guía de Configuración Rápida

## Configuración Inicial

### 1. Crear la Base de Datos
```bash
mysql -u root -p < DB/Tables.sql
```

### 2. Crear la Cuenta de Administrador Inicial
```bash
python setup_admin.py
```

Esto creará una cuenta de administrador con:
- **Email**: `admin@admin.com`
- **Contraseña**: `admin123`

### 3. Iniciar la Aplicación
```bash
python App.py
```

### 4. Iniciar Sesión
1. Ir a: http://127.0.0.1:5000
2. Click en "Iniciar Sesión como Alumno" (o cualquier opción de login)
3. Ingresar:
   - Email: `admin@admin.com`
   - Contraseña: `admin123`
4. Serás redirigido al Dashboard de Administrador

### 5. Crear Más Usuarios
Una vez iniciado sesión como admin, puedes:
- Crear Alumnos: `/alumnos/nuevo`
- Crear Docentes: `/docentes/nuevo`
- Gestionar usuarios: `/usuarios`

## Credenciales de Admin por Defecto

⚠️ **Advertencia de Seguridad**: Cambiar la contraseña por defecto después del primer login!

- **Email**: `admin@admin.com`
- **Contraseña**: `admin123`
- **CI**: `000ADMIN`

## Solución de Problemas

### "Cannot access dashboard without account"
Este es el **comportamiento de seguridad correcto**. Necesitas:
1. Ejecutar `setup_admin.py` para crear la primera cuenta de admin
2. Iniciar sesión con las credenciales de admin
3. Luego crear otros usuarios desde el dashboard de admin

### "ModuleNotFoundError: No module named 'flask_wtf'"
```bash
pip install Flask-WTF email-validator
```

### Error de Conexión a Base de Datos
- Verificar que MySQL está corriendo
- Verificar que la base de datos `OBL` existe
- Revisar credenciales en `Connector.py` o variables de entorno

