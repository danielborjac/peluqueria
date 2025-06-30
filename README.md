## Instrucciones para levantar el backend de Django

1. Clona el repositorio.
2. Crear base de datos con los respectivos comandos:
    a. acceder a MySQL con el comando: mysql -u <tu usuario> -p
    b. ingresa tu contraseña
    c. crear la base con el comando: CREATE DATABASE dpelos;
3. Instalar dependencias: pip install -r requirements.txt
4. Ejecutar migraciones:
    a. python manage.py makemigration
    b. python manage.py migrate
5. (Opcional) cargar datos por defecto: python manage.py loaddata data.json
6. Correr el servidor: python manage.py runserver
