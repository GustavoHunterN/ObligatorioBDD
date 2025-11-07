# 📘 Obligatorio BDD — Backend & Data Integration

## 📊 Diagrama ER 
Se diseñó un diagrama basado en las estructuras sugeridas en la letra del enunciado.  
Cada entidad se representa con un **rectángulo naranja**,  
las **Primary Keys** en **mayúsculas**, y las **Foreign Keys** con flechas desde el atributo hacia la entidad de referencia.  

El diseño prioriza la claridad visual y la trazabilidad de relaciones para facilitar la implementación posterior en el backend.

---

## 🧩 Database
Algunas entidades (como **Facultad** y **Reserva**) requieren que sus IDs sean generadas desde el backend.  
Esto permite crear claves más legibles y manejables mediante los métodos `__str__` y `__repr__`,  
manteniendo el código más sustentable y eficiente a largo plazo.  

La estructura final de la base incluye control de claves foráneas, relaciones jerárquicas y restricciones de dominio.  
El esquema completo fue ajustado para garantizar compatibilidad con el backend Python y MySQL.  

---

## 🧠 Diagrama UML
El diagrama UML fue diseñado en base a las clases que reflejan el modelo relacional.  
Cada clase mantiene una relación directa con su tabla equivalente en la base,  
respetando composición, herencia y dependencia entre entidades.  

Se priorizó la legibilidad del flujo jerárquico de objetos y la consistencia entre atributos de clase y columnas SQL.

---

## 🔐 Seguridad
Las contraseñas de los usuarios serán almacenadas de forma **encriptada** (no en texto plano).  
La clase `Sancion` se instancia desde un método interno dentro de `Participante`,  
siguiendo principios de **encapsulamiento y responsabilidad única**.  

Se prevé aplicar el mismo enfoque en otras relaciones de composición para mantener cohesión y control de lógica de negocio.  

---

## 🧱 Clases
Las clases fueron desarrolladas para reflejar la estructura de la base de datos y optimizar la interacción con ella.  
Inicialmente se diseñaron sin métodos, para luego integrarse con el backend a través del archivo `main.py`.  

Cada clase incluye:
- Atributos que reflejan los campos de la tabla correspondiente.
- Métodos `save()` que insertan registros directamente en MySQL mediante la clase `Conexion`.
- Relaciones entre objetos que respetan las Foreign Keys (por ejemplo, `Sala` depende de `Edificio`, `Reserva` depende de `Turnos`, etc.).

La lógica de inserción en cascada permite construir jerarquías completas desde el backend sin depender de autoincrementos externos.

---

## ⚙️ 06/11 — Implementación de Control y Backend Inicial

Se crearon los módulos `control.py` y `BE.py`.

### `control.py`
Contiene los diccionarios de apoyo:
- **`dtypes`**: define los tipos de datos y dominios válidos por clase y atributo.
- **`n_of_instances`**: controla las instancias por entidad y permite generar claves personalizadas (por ejemplo, *Sala en edificio Mullin → M001*).

Esto permite mantener control lógico desde el backend y asegurar unicidad de claves sin depender del autoincremento.

### `BE.py`
Centraliza la ejecución y validación de inserciones, además de integrar los controladores con la base de datos.  

El esquema SQL fue reformado para aceptar claves controladas desde Python, manteniendo consistencia en las relaciones.

---

## ⚙️ 07/11 — Integración Clases ↔ Base de Datos

Se completó la integración total entre el modelo orientado a objetos y la base relacional, logrando:
- Simetría entre nombres de atributos y columnas.
- Consistencia entre tipos de datos y claves foráneas.

### Backend
Se implementaron los métodos `save()` en todas las clases,  
permitiendo interacción directa con MySQL mediante `Conexion`.  
Cada inserción ejecuta un `commit` automático y retorna, cuando corresponde, el `lastrowid` asignado.

El flujo jerárquico de creación de entidades quedó definido de la siguiente forma:
- `Edificio` → `Sala` → `Turnos` → `Reserva`
- `Participante` → `ReservaParticipante`
- `Facultad` → `Programa` → `ParticipantePrograma`

### `main.py`
Se agregó un flujo de prueba completo que permite crear y relacionar objetos en orden lógico,  
validando la integridad de las Foreign Keys y la consistencia del modelo.

### `control.py`
Sigue administrando los tipos y contadores de instancias (`dtypes`, `n_of_instances`),  
permitiendo la futura automatización de IDs con prefijos específicos (ej. `M001` para las salas del edificio *Mullin*).

---

## 📋 To Do (actualizado)

- Implementar método `idmaker` para generación automática de IDs por entidad.  
- Crear usuarios y permisos específicos en MySQL para aislar roles **Admin / User**.  
- Añadir métodos `fetch()` con condiciones en cada clase (consultas dinámicas desde backend).  
- Desarrollar endpoints CRUD mediante Flask para exponer el backend como API REST.  
- Integrar encriptación de contraseñas (bcrypt o hashlib).  

---


## FRONT 
Las clases de clases.jpg que tienen atributo:[tipo de dato], tienen un dominio limitado.
Deberían ser un desplegable.  
Para buscar que mostrar en el desplegable buscar en el diccionario llamado dtypes de control.py 

EJ :  
Si se esta haciendo el formulario de Sala:  
import control   
desplegable = control.dtypes["Sala"]["tipo"]  
Obtendrá una lista con los datos a elegir. 




  Formularios. 

- Registro Usuario 

 - Login Usuario 

- Registro Edificios(añadir número de Salas Total)

- Registro de Programas. 

- Registro de Facultades.


Pages: 

Home Page para Admin 
- Una barra lateral que una pestaña pueda acceder a registrar edificios, Facultades, Reservas y participantes. 
- Otra pestaña para acceder a editar los ya existentes de cada entidad. (devuelve una tabla editable).

Home Page para User 
- Una barra lateral que una pestaña sea tan solo de registro de Reservas (elige un dia en el calendario y una sala, devuelve una tabla de horarios, y puede poner el check en el horario elegido)
- Una pestaña de reservas activas. Devuelve una tabla con las reservas activas, teniendo un botón para ver las reservas antiguas también. 
