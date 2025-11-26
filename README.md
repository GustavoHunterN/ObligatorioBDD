# Sistema de Gestión de Reservas de Salas - OBL

Sistema web para la gestión de reservas de salas académicas desarrollado con Flask y MySQL.

## 📋 Características

- **Gestión de Usuarios**: Administradores, Docentes y Alumnos
- **Reservas de Salas**: Sistema completo de reservas con validaciones
- **Programas Académicos**: Inscripción de participantes a programas
- **Sanciones**: Sistema de sanciones para participantes
- **Business Intelligence**: Reportes y análisis de datos (solo Admin)
- **Seguridad**: Protección CSRF, validación de datos, acceso por roles

## 🚀 Inicio Rápido con Docker

### Requisitos Previos

- Docker y Docker Compose instalados
- Git (opcional, para clonar el repositorio)

### Pasos de Instalación

1. **Clonar o descargar el proyecto**
   ```bash
   git clone <url-del-repositorio>
   cd ObligatorioBDD
   ```

2. **Iniciar los contenedores**
   ```bash
   docker-compose up -d
   ```

3. **Esperar a que la base de datos se inicialice** (30-60 segundos)

4. **Crear cuenta de administrador inicial**
   ```bash
   docker-compose exec web python setup_admin.py
   ```

5. **Acceder a la aplicación**
   - Abrir navegador en: `http://localhost:5000`
   - Credenciales de admin:
     - **Email**: `admin@admin.com`
     - **Contraseña**: `admin123`

### Comandos Útiles

```bash
# Ver logs de la aplicación
docker-compose logs -f web

# Ver logs de la base de datos
docker-compose logs -f db

# Detener los contenedores
docker-compose down

# Detener y eliminar volúmenes (borra la base de datos)
docker-compose down -v

# Reiniciar los contenedores
docker-compose restart
```

## 🛠️ Instalación Manual (Sin Docker)

### Requisitos

- Python 3.11 o superior
- MySQL 8.0 o superior
- pip (gestor de paquetes de Python)

### Pasos

1. **Clonar el repositorio**
   ```bash
   git clone <url-del-repositorio>
   cd ObligatorioBDD
   ```

2. **Crear entorno virtual**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar base de datos MySQL**
   ```bash
   # Conectar a MySQL como root
   mysql -u root -p
   
   # Ejecutar script de inicialización
   source DB/init.sql
   
   # Crear cuenta de administrador
   source DB/crear_admin.sql
   ```

5. **Configurar variables de entorno** (opcional)
   ```bash
   export DB_HOST=localhost
   export DB_USER=appuser
   export DB_PASSWORD=securepassword
   export DB_NAME=OBL
   ```

6. **Ejecutar la aplicación**
   ```bash
   python App.py
   ```

7. **Acceder a la aplicación**
   - Abrir navegador en: `http://localhost:5000`
   - Credenciales de admin:
     - **Email**: `admin@admin.com`
     - **Contraseña**: `admin123`

## 👥 Roles del Sistema

### Administrador
- Gestión completa de usuarios, salas, edificios, facultades y programas
- Visualización de todas las reservas
- Gestión de sanciones
- Acceso a reportes de Business Intelligence

### Docente
- Crear reservas para programas asignados
- Pasar lista de asistencia
- Ver sus propias reservas
- Inscribirse a programas

### Alumno
- Crear reservas para programas asignados
- Ver sus propias reservas
- Inscribirse a programas

## 📁 Estructura del Proyecto

```
ObligatorioBDD/
├── App.py                 # Aplicación principal Flask
├── Connector.py           # Conexión a base de datos
├── Clases.py              # Modelos de datos
├── control.py             # Lógica de negocio
├── modules/               # Módulos de la aplicación
│   ├── auth.py           # Autenticación
│   ├── dashboard.py      # Dashboards por rol
│   ├── reservas.py       # Gestión de reservas
│   ├── programas.py      # Gestión de programas
│   ├── usuarios.py       # Gestión de usuarios
│   ├── salas.py          # Gestión de salas
│   ├── edificios.py      # Gestión de edificios
│   ├── sanciones.py      # Gestión de sanciones
│   ├── bi.py             # Business Intelligence
│   ├── forms.py          # Formularios Flask-WTF
│   ├── security.py       # Validaciones de seguridad
│   └── validation.py     # Validación de datos
├── templates/             # Plantillas HTML
├── DB/                    # Scripts SQL
│   ├── init.sql          # Inicialización completa
│   └── crear_admin.sql   # Crear cuenta admin
├── docker-compose.yml     # Configuración Docker
├── Dockerfile            # Imagen Docker de la app
└── requirements.txt      # Dependencias Python
```

## 🔐 Seguridad

- **Protección CSRF**: Todos los formularios están protegidos
- **Validación de entrada**: Sanitización y validación de todos los datos
- **Acceso por roles**: Middleware para control de acceso
- **Usuario de BD con privilegios mínimos**: Solo SELECT, INSERT, UPDATE, DELETE
- **Consultas parametrizadas**: Prevención de inyección SQL

## 🐛 Solución de Problemas

### Error: "Access denied for user 'appuser'"
- Verificar que el usuario `appuser` existe en MySQL
- Verificar credenciales en variables de entorno
- En Docker, las credenciales están en `docker-compose.yml`

### Error: "Database 'OBL' doesn't exist"
- Ejecutar `DB/init.sql` para crear la base de datos
- En Docker, esto se hace automáticamente

### Error: "The CSRF token is missing"
- Asegurarse de que todos los formularios incluyen `{{ csrf_token() }}`
- Verificar que Flask-WTF está instalado

### La aplicación no inicia
- Verificar que MySQL está corriendo
- Verificar variables de entorno
- Revisar logs: `docker-compose logs web`

## 📄 Licencia

Este proyecto es parte de un trabajo académico.
