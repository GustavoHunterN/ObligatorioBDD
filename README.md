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