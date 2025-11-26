# Inicio Rápido: Configuración de Seguridad de Base de Datos

## Paso 1: Crear el Usuario de la Aplicación

Ejecutar como usuario root de MySQL:
```bash
mysql -u root -p < DB/create_app_user.sql
```

O manualmente:
```sql
mysql -u root -p
source DB/create_app_user.sql
```

## Paso 2: Actualizar Configuración de la Aplicación

La aplicación ya está configurada para usar el nuevo usuario. Por defecto, usará:
- Usuario: `appuser`
- Contraseña: `securepassword`
- Host: `localhost`
- Base de datos: `OBL`

## Paso 3: Configurar Variables de Entorno (Opcional pero Recomendado)

Para producción, configurar variables de entorno:

```bash
export DB_USER='appuser'
export DB_PASSWORD='tu_contraseña_segura'
export DB_HOST='localhost'
export DB_NAME='OBL'
```

O crear un archivo `.env` (no commitear a git):
```
DB_USER=appuser
DB_PASSWORD=tu_contraseña_segura
DB_HOST=localhost
DB_NAME=OBL
```

## Paso 4: Verificar Instalación

Probar la conexión:
```python
from Connector import Conexion
con = Conexion()
print("Conexión exitosa!")
con.cerrar()
```

Verificar privilegios:
```sql
mysql -u root -p
SHOW GRANTS FOR 'appuser'@'localhost';
```

## Solución de Problemas

### Error: Access denied
- Verificar que el usuario fue creado: `SELECT User, Host FROM mysql.user WHERE User='appuser';`
- Verificar que la contraseña es correcta
- Verificar si el usuario tiene privilegios: `SHOW GRANTS FOR 'appuser'@'localhost';`

### Error: Table access denied
- Verificar que los grants fueron aplicados: `SHOW GRANTS FOR 'appuser'@'localhost';`
- Re-ejecutar `create_app_user.sql` si es necesario

### La conexión funciona pero las operaciones fallan
- Verificar que FLUSH PRIVILEGES fue ejecutado
- Verificar que los nombres de tablas coinciden exactamente (sensible a mayúsculas)

## Checklist de Seguridad

- [ ] Usuario `appuser` creado
- [ ] Contraseña fuerte configurada (no 'securepassword')
- [ ] Privilegios otorgados en las 11 tablas
- [ ] FLUSH PRIVILEGES ejecutado
- [ ] Aplicación probada con el nuevo usuario
- [ ] Variables de entorno configuradas (producción)
- [ ] Archivo `.env` creado y agregado a `.gitignore` (si se usa)

