# Integrar tareas de celery con django

1. Clonamos en repositorio

```sh
git clone https://github.com/hanzbk/tareascelery
```

2. Ingresamos al entorno virual
```sh
source celery_env/bin/bash
```

3. Instalamos las librerias necesarias
```sh
sudo apt-get install rabbitmq-server #gestión y ejecutor de tareas
pip3 install celery  #inicia, encola tareas
pip3 install django-celery-results #Seguimiento y guardado de tareas en django
```

4. Configuramos el proyecto para que ejecute celery
   - Vamos al archivo settings.py y en  INSTALLED_APPS agregamos celery y django_celery_results

                #Celery
                'celery',
                'django_celery_results',
   - Configuramos la zona horaria de celery

                CELERY_TIMEZONE = 'America/Bogota'
                
   - Agregamos las variables necesarios de Celery que nos ayudan a la ejecución y comunicación con el broker
     ```sh
     ### Configuración de Celery
     BROKER_URL = 'amqp://guest:guest@localhost//'
     CELERY_RESULT_BACKEND = 'django-db'
     CELERY_CACHE_BACKEND = 'django-cache'
     CELERY_ACCEPT_CONTENT = ['application/json']
     CELERY_TASK_SERIALIZER = 'json'
     CELERY_RESULT_SERIALIZER = 'json'
     ```

   - En la raiz del proyecto, al nivel de settings.py, creamos el archivo celery.py y agregamos
     ```sh
     #Activamos los imports absolutos para evitar conflictos entre packages
     from __future__ import absolute_import
     import os
     from celery import Celery
     from django.conf import settings

     os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tareascelery.settings')
     app = Celery('tareascelery')
     
     app.config_from_object('django.conf:settings')
     
     app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

     @app.task(bind=True)
     def debug_task(self):
        print('Request: {0!r}'.format(self.request))
     ```

   - Al mismo nivel del archivo settings.py y celery.py, entramos al archivo __init__.py y agregamos las siguientes lineas
     ```sh
     from __future__ import absolute_import
     from .celery import app as celery_app
     ```
   - Dentro del app, al nivel de views.py y models.py creamos el archivo tasks.py en donde se ubicaran todas la tareas que se ejecutarán desde la vista, y ponemos estas tareas de ejemplo
     **Nota:** @shared_task es el decorador que nos indica que esa función es una tarea
     ```sh
     from __future__ import absolute_import
     from celery import shared_task
     @shared_task

     def add(x, y):
         return x + y

     @shared_task
     def mul(x, y):
         return x * y
                
     @shared_task
     def xsum(numbers):
         return sum(numbers)
     ```

5. Ejecución

   - Migracion de django-celery-results
     ```sh
     python3 manage.py migrate
     ```
   - Ejecutar celery
     ```sh
     celery -A tareascelery worker -l info
     ```
   - Ejecutar Django
     ```sh
     python3 manage.py shell
     ```
     - Ejecutaremos una tarea en la consola del power sheel

     - Importamos una de la stareas de nuestro archivo tasks, en este caso add
       ```sh
       from tareas.tasks import add
       ```
     - Usamos delay para realizar la ejecución de una tarea. Enviamos la tarea con los parametro, en esta caso dos numeros para realizar la suma
       ```sh
       resultado = add.delay(2,3)
       ```        
     - Podemos observar en la consola que se ejecuto celery que retorna la suma de estos dos numero

6. Practica

   - Cambiando el python3 manage.py shell por python3 manage.py runserver
   - Vamos al archivo tasks y creamos una nueva función que nos recorre un numero dado
     ```sh
     @shared_task
     def recorrer(valor):
         i=0
         while i <= valor:
             print('i',i)
             i=i+1
             time.sleep(10)
         return 'Recorrio el valor '+str(valor)
     ```        
   - Importamos la tareas en nuestra vista
     ```sh
     from .tasks import recorrer, add, mul, xsum
     ```
   - Creamos nuestra función para la vista, enviamos el numero 10 como argumento y ejecutamos la tarea con delay
     ```sh
     def recorrer_numero(request):
         resultado= recorrer.delay(10)
     ```
     Cuando ejecutamos esta funcion, vemos que la consola de celery empieza a ejecutarse

   - Enviar varias tareas en diferentes workers y distribuirlas

     - Detenemos celery y abrimos 3 consolas adicionales, en cada una ponemos los siguientes comandos
       **Nota:** -concurrency= es el numero de tareas que se pueden ejecutar simultaneamente en cada worker
       ```sh
       Consola 1: debe estar ejecutando el runserver  python3 manage.py runserver
       Consola 1: celery -A tareascelery worker -l info --concurrency=4 -n worker1@%h
       Consola 1: celery -A tareascelery worker -l info --concurrency=4 -n worker2@%h
       Consola 1: celery -A tareascelery worker -l info --concurrency=4 -n worker3@%h
       Consola 1: celery -A tareascelery worker -l info --concurrency=4 -n worker4@%h
       ```
     - Agregaremos a nuestra vista la ejecución a las otras 3 tareas restantes
       ```sh
       def recorrer_numero(request):
           resultado= recorrer.delay(10)
           add.delay(2,8)
           mul.delay(3,5)
           xsum.delay([3,4,5,6])
       ```       
     - Ejecutamos la vista y vemos como cada tarea es atendida por cada uno de los workers. La filosofia es:
       - Tarea recorrer, va al worker1, esta desocupado, ejecuta
       - Tarea delay, va al worker1, esta ocupado, va al worker2, esta desocupado, ejecuta
       - Tarea recorrer, va al worker1, esta ocupado, va al worker2, esta ocupado, va al worker3, esta desocupado, ejecuta
       - Tarea recorrer, va al worker1, esta ocupado, va al worker2, esta ocupado, va al worker3, esta odupado, va al worker4, esta desocupado, ejecuta

    





