### Diagrama ER 

Para comenzar se diseñó un diagrama con las 
estructuras sugeridas en la letra.  
Denotando cada Entidad con un Rectángulo Naranja. Cada
Primary Key con Mayúsculas y cada Foreign Key con una 
flecha desde el atributo hacia la entidad. 

### Database
Las ID de algunas entidades como Facultad y Reserva van a tener que ser reformuladas e introducidas 
desde BackEnd. Para hacerlas más legibles con un str o repr. Pensando en manutención del codigo y 
optimizar el tiempo al desarrollarlo. 



### Diagrama UML
Se diseñó el diagrama UML con las clases que satisfacen las necesidades  
del DataBase. 

### ˜
Se planea que las contraseñas sean encriptadas y no texto plano. 

Se decidió que la clase sancion sea creada desde un metodo adentro de participante. 
Para mantentener un encapsulamiento adecuado.  
Se teoriza que será necesario implementar esta práctica en algunas sino todas las relaciones de composicion. 
Se verá mas adelante. 



### Clases 

Se hace primero las clases sin metodos, 
una vez se comience con el main se verá los metodos
a implementar

Se confirmó con un script que las repr y str están bien implementadas. 


### 06/11

Se hicieron control.py y BE.py 

control.py conteniendo diccionarios utiles para
las funcionalidades. 
Como un contador de instancias para crear las keys
(Sala en edicio Mullin: M001).  
Esto con el fin de controlar Las Keys desde BE. 

También uno de tipos de datos. Con su clase, el atributo y el dominio de este. 

Se reformó el DB para Insertar keys desde backend para que sean unicas.  
Al ser FK's no pueden ser un AUTOINCREMENT simple. 




### to do 

- Falta ID programa en Clases y DB

- Faltan métodos "idmaker"  
 ej { Sala : {Edificio.nombre : }} entonces {inicial_edificio} + "sal"+ {cantidad_de_instancias}
- Hacer usuario y permisos en la base de datos. 


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
