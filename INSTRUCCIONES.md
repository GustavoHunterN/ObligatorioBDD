# 📖 Instrucciones de Uso - Sistema de Gestión de Reservas OBL

## 🚀 Inicio Rápido

### Opción 1: Usar Docker (Recomendado)

1. **Asegúrate de tener Docker y Docker Compose instalados**
   ```bash
   docker --version
   docker-compose --version
   ```

2. **Inicia los contenedores**
   ```bash
   docker-compose up -d
   ```

3. **Espera 30-60 segundos** para que la base de datos se inicialice

4. **Verifica que todo esté funcionando**
   ```bash
   docker-compose logs web
   ```

5. **Accede a la aplicación**
   - Abre tu navegador en: `http://localhost:5000`
   - Credenciales de administrador:
     - **Email**: `admin@admin.com`
     - **Contraseña**: `admin123`

### Opción 2: Instalación Manual

1. **Instala Python 3.11+ y MySQL 8.0+**

2. **Crea un entorno virtual**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. **Instala dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configura la base de datos**
   ```bash
   mysql -u root -p < DB/init.sql
   mysql -u root -p < DB/crear_admin.sql
   ```

5. **Configura variables de entorno** (opcional)
   ```bash
   export DB_HOST=localhost
   export DB_USER=appuser
   export DB_PASSWORD=securepassword
   export DB_NAME=OBL
   ```

6. **Ejecuta la aplicación**
   ```bash
   python App.py
   ```

7. **Accede a la aplicación**
   - Abre tu navegador en: `http://localhost:5000`

## 👤 Primeros Pasos

### 1. Iniciar Sesión como Administrador

1. Ve a `http://localhost:5000`
2. Haz clic en "Iniciar Sesión como Administrador" o usa cualquier formulario de login
3. Ingresa:
   - **Email**: `admin@admin.com`
   - **Contraseña**: `admin123`

### 2. Crear Usuarios

Como administrador, puedes crear:
- **Alumnos**: Desde el menú "Usuarios" → "Crear Alumno"
- **Docentes**: Desde el menú "Usuarios" → "Crear Docente"

### 3. Crear Estructura Académica

1. **Crear Facultades**: "Configuración" → "Facultades" → "Nueva Facultad"
2. **Crear Programas**: "Configuración" → "Programas" → "Nuevo Programa"
3. **Crear Edificios**: "Configuración" → "Edificios" → "Nuevo Edificio"
4. **Crear Salas**: "Configuración" → "Salas" → "Nueva Sala"

### 4. Inscribir Usuarios a Programas

1. Ve a "Usuarios" → "Listar Usuarios"
2. Selecciona un usuario
3. Haz clic en "Ver Programas" o "Inscribir a Programa"

## 📋 Funcionalidades por Rol

### Administrador

- ✅ Gestión completa de usuarios (crear, editar, eliminar)
- ✅ Gestión de edificios y salas
- ✅ Gestión de facultades y programas
- ✅ Visualización de todas las reservas
- ✅ Gestión de sanciones
- ✅ Reportes de Business Intelligence
- ✅ Inscribir usuarios a programas

### Docente

- ✅ Crear reservas para programas asignados
- ✅ Pasar lista de asistencia
- ✅ Ver sus propias reservas
- ✅ Editar sus reservas (fecha y turno)
- ✅ Inscribirse a programas

### Alumno

- ✅ Crear reservas para programas asignados
- ✅ Ver sus propias reservas
- ✅ Editar sus reservas (fecha y turno)
- ✅ Inscribirse a programas

## 🔧 Comandos Útiles de Docker

```bash
# Ver logs en tiempo real
docker-compose logs -f web

# Ver logs de la base de datos
docker-compose logs -f db

# Detener los contenedores
docker-compose down

# Detener y eliminar volúmenes (borra la base de datos)
docker-compose down -v

# Reiniciar los contenedores
docker-compose restart

# Reconstruir las imágenes
docker-compose build

# Ejecutar comandos dentro del contenedor
docker-compose exec web python setup_admin.py
```

## 🐛 Solución de Problemas

### La aplicación no inicia

1. **Verifica que los contenedores estén corriendo**
   ```bash
   docker-compose ps
   ```

2. **Revisa los logs**
   ```bash
   docker-compose logs web
   ```

3. **Verifica que el puerto 5000 no esté en uso**
   ```bash
   lsof -i :5000  # En macOS/Linux
   netstat -ano | findstr :5000  # En Windows
   ```

### Error de conexión a la base de datos

1. **Verifica que MySQL esté corriendo**
   ```bash
   docker-compose ps db
   ```

2. **Verifica las variables de entorno**
   ```bash
   docker-compose exec web env | grep DB_
   ```

3. **Reinicia los contenedores**
   ```bash
   docker-compose restart
   ```

### No puedo iniciar sesión

1. **Verifica que el usuario admin exista**
   ```bash
   docker-compose exec web python setup_admin.py
   ```

2. **Verifica las credenciales**
   - Email: `admin@admin.com`
   - Contraseña: `admin123`

### La base de datos está vacía

1. **Ejecuta el script de inicialización**
   ```bash
   docker-compose exec db mysql -u root -prootpassword < /docker-entrypoint-initdb.d/init.sql
   ```

2. **O reinicia los contenedores con volúmenes limpios**
   ```bash
   docker-compose down -v
   docker-compose up -d
   ```

## 📝 Notas Importantes

- ⚠️ **Cambiar contraseñas por defecto** en producción
- ⚠️ **Configurar variables de entorno** para credenciales de BD en producción
- ⚠️ **Hacer backup regular** de la base de datos
- ✅ El usuario admin puede iniciar sesión desde cualquier formulario de login
- ✅ Los turnos están predefinidos de 8:00 a 22:00 (cada hora)

## 🔐 Seguridad

- Todos los formularios están protegidos con CSRF
- Las consultas SQL usan parámetros para prevenir inyección
- El usuario de BD tiene privilegios mínimos (solo SELECT, INSERT, UPDATE, DELETE)
- Los datos de entrada se validan y sanitizan

## 📞 Soporte

Para problemas o consultas:
1. Revisa los logs: `docker-compose logs`
2. Verifica la documentación en `README.md`
3. Contacta al equipo de desarrollo

