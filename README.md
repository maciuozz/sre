# Practica SRE Paolo Scotto Di Mase
Se han agregado 2 endpoints, 2 contadores y 2 pruebas unitarias que están señalizados de manera visible en el codigo.
Observamos la ejecución de los 4 tests con el informe de cobertura de código:

    (venv) 21:33 @/Users/paoloscotto/desktop/sre ~ (git)-[main] $ pytest --cov
    =============================================================== test session starts ================================================================
    platform darwin -- Python 3.9.6, pytest-7.1.1, pluggy-1.0.0 -- /Users/paoloscotto/Desktop/SRE/venv/bin/python3
    cachedir: .pytest_cache
    rootdir: /Users/paoloscotto/Desktop/SRE, configfile: pytest.ini, testpaths: src/tests/
    plugins: asyncio-0.18.3, anyio-3.6.2, cov-3.0.0
    asyncio: mode=auto
    collected 4 items

    src/tests/app_test.py::TestSimpleServer::read_health_test PASSED                                                                             [ 25%]
    src/tests/app_test.py::TestSimpleServer::read_main_test PASSED                                                                               [ 50%]
    src/tests/app_test.py::TestSimpleServer::bye_bye_test PASSED                                                                                 [ 75%]
    src/tests/app_test.py::TestSimpleServer::joke_endpoint_test PASSED                                                                           [100%]

    ---------- coverage: platform darwin, python 3.9.6-final-0 -----------
    Name                          Stmts   Miss Branch BrPart     Cover   Missing
    ----------------------------------------------------------------------------
    src/application/__init__.py       0      0      0      0   100.00%
    src/application/app.py           44      5      4      1    87.50%   31, 35-37, 77
    src/tests/__init__.py             0      0      0      0   100.00%
    src/tests/app_test.py            32      0      2      0   100.00%
    ----------------------------------------------------------------------------
    TOTAL                            76      5      6      1    92.68%

    Required test coverage of 80.0% reached. Total coverage: 92.68%

    ================================================================ 4 passed in 1.69s =================================================================
    
<img width="1790" alt="Screenshot 2023-04-25 at 21 38 59" src="https://user-images.githubusercontent.com/118285718/234386277-b5564adc-950b-4157-a180-aebbb8e2f19d.png">

Se ha creado una pipeline mediante GitHub Actions que hace uso de 2 archivos, ***test.yaml*** y ***release.yaml***, los cuales representan 2 flujos de trabajo/workflow o fases distintas. La fase de release se activa cuando se verifica un push de tag que comienza con la letra "v". Por otro lado, la fase de test se activa con push de código o pull requests (PR). He usado un repositorio privado en mi cuenta personal de GitHub en vez de usar un repositorio dentro de la organización ***keepcodingclouddevops7*** como vimos durante las clases.
El fichero ***release.yaml*** usa 3 ***repository secret***: ***GHCR_PAT***, ***DOCKERHUB_TOKEN*** y ***DOCKERHUB_USERNAME***.
Para definir ***GHCR_PAT*** generamos un token en ***Settings*** --> ***Developer settings*** con estos permisos:  

<img width="1187" alt="Screenshot 2023-04-24 at 02 12 21" src="https://user-images.githubusercontent.com/118285718/233874655-ca1eb09a-7908-43d2-a032-f1ba8db3fbe3.png">

Dentro del repositorio generamos un secret, ***GHCR_PAT***, en ***Settings*** --> ***Secrets and variables*** --> ***Actions*** con el valor del PAT creado anteriormente. Para definir ***DOCKERHUB_TOKEN*** generamos un token en Docker Hub y usamos su valor para crear el secret. Para definir
***DOCKERHUB_USERNAME*** simplemente creamos un secret con el valor del nombre de usuario de Docker Hub. A continuación se muestran los 3 secret:

<img width="1224" alt="Screenshot 2023-04-24 at 02 24 56" src="https://user-images.githubusercontent.com/118285718/233875331-b1faa951-b2cb-40e8-a741-0ac7ccf365ff.png">

Para desplegar Prometheus creamos un cluster de Kubernetes que utilice la versión v1.21.1 utilizando minikube para ello a través de un nuevo perfil llamado monitoring-demo:

    minikube start --kubernetes-version='v1.21.1' --memory=4096 --addons="metrics-server -p monitoring-demo

Añadir el repositorio de helm prometheus-community para poder desplegar el chart kube-prometheus-stack:

    helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
    helm repo update

Desplegar el chart kube-prometheus-stack del repositorio de helm añadido en el paso anterior con los valores configurados en el archivo kube-prometheus-stack/values.yaml en el namespace monitoring:

    helm -n monitoring upgrade --install prometheus prometheus-community/kube-prometheus-stack -f kube-prometheus-stack/values.yaml --create-namespace --wait --version 34.1.1
    
Para ver los pod en el namespace monitoring utilizado para desplegar el stack de prometheus: 

    kubectl -n monitoring get po -w

Desplegamos nuestra aplicación que utiliza [FastAPI](https://fastapi.tiangolo.com/) para levantar un servidor en el puerto 8081 utilizando Helm:

    helm install my-release helm-chart-simple-server/ -n monitoring

Deberiamos obtener este output:

    NAME: my-release
    LAST DEPLOYED: Tue Apr 25 16:24:40 2023
    NAMESPACE: monitoring
    STATUS: deployed
    REVISION: 1
    NOTES:
    1. Get the application URL by running:
       - kubectl port-forward service/my-release-simple-server 8081:8081
      
Despues de ejecutar el ***port-forward*** mencionado en la sección ***NOTES*** del output anterior, comprobamos que la aplicación funcione correctamente accediendo a ***"/joke"***:

<img width="1041" alt="Screenshot 2023-04-25 at 17 42 04" src="https://user-images.githubusercontent.com/118285718/234331009-4df67f90-ede7-4667-b85d-5fd2aadf70e8.png">
<img width="941" alt="Screenshot 2023-04-25 at 17 40 29" src="https://user-images.githubusercontent.com/118285718/234331026-19f9d49a-285b-43eb-8448-3849f229e323.png">
<img width="955" alt="Screenshot 2023-04-25 at 17 38 16" src="https://user-images.githubusercontent.com/118285718/234331164-ec9d1550-14d0-434b-8828-91d50fcab993.png">
<img width="801" alt="Screenshot 2023-04-25 at 17 34 47" src="https://user-images.githubusercontent.com/118285718/234329056-5417df98-f439-41e3-ad49-c70b905f887e.png">

Realizamos una prueba de estrés utilizando [Vegeta](https://github.com/tsenart/vegeta/releases). Podemos ejecutar este comando repetidas veces (el endpoint se puede cambiar: ***"/health", "/bye", "/joke")***:

    echo "GET http://localhost:8081" | vegeta attack -rate=500 -duration=60s | vegeta report

El output del comando anterior debería ser similar a:

    16:37 @/Users/paoloscotto/desktop/sre ~ (git)-[main] $ echo "GET http://localhost:8081" | vegeta attack -rate=500 -duration=60s | vegeta report
    Requests      [total, rate, throughput]         30000, 500.02, 105.72
    Duration      [total, attack, wait]             1m5s, 59.998s, 4.91s
    Latencies     [min, mean, 50, 90, 95, 99, max]  29.164µs, 495.362ms, 99.3µs, 2.087s, 2.579s, 3.742s, 7.405s
    Bytes In      [total, mean]                     144102, 4.80
    Bytes Out     [total, mean]                     0, 0.00
    Success       [ratio]                           22.87%
    Status Codes  [code:count]                      0:23138  200:6862
    Error Set:
    Get "http://localhost:8081": dial tcp: lookup localhost: no such host
    Get "http://localhost:8081": dial tcp 0.0.0.0:0->[::1]:8081: socket: too many open files
    
Como que hemos configurado prometheus para que nos envíe notificaciones a Slack si la tasa promedio de uso de CPU es mayor que la cantidad promedio de CPU solicitada por el contenedor, despues de unos minutos deberíamos observar:

<img width="1792" alt="Screenshot 2023-04-25 at 20 54 20" src="https://user-images.githubusercontent.com/118285718/234376318-b246d27a-9941-4d87-85a5-52d077ac5dc2.png">

Aqui podemos observar el escalado/desescalado horizontal: 

    20:37 @/Users/paoloscotto/desktop/sre ~ (git)-[main] $ k get pod -n monitoring -w | grep simple
    my-release-simple-server-7f89c4969b-ft57s                1/1     Running   0          13m
    my-release-simple-server-7f89c4969b-htrf2                1/1     Running   0          13m
    my-release-simple-server-7f89c4969b-ndnrv                1/1     Running   0          15m
    my-release-simple-server-7f89c4969b-t4zbj                1/1     Running   0          13m
    my-release-simple-server-7f89c4969b-t4zbj                1/1     Terminating   0          16m
    my-release-simple-server-7f89c4969b-t4zbj                0/1     Terminating   0          17m
    my-release-simple-server-7f89c4969b-t4zbj                0/1     Terminating   0          17m
    my-release-simple-server-7f89c4969b-t4zbj                0/1     Terminating   0          17m
    my-release-simple-server-7f89c4969b-t4zbj                0/1     Terminating   0          17m

Para ver la salida de las métricas de Prometheus expuestas por la aplicación ejecutamos: 

    kubectl -n monitoring port-forward service/my-release-simple-server 8000:8000

Con http://localhost:8000/:

    # HELP main_requests_total Total number of requests to main endpoint
    # TYPE main_requests_total counter
    main_requests_total 172089.0
    # HELP bye_requests_total Total number of requests to bye endpoint
    # TYPE bye_requests_total counter
    bye_requests_total 7082.0
    # HELP joke_requests_total Total number of requests to joke endpoint
    # TYPE joke_requests_total counter
    joke_requests_total 15.0

Abrir una nueva pestaña en la terminal y realizar un port-forward del puerto http-web del servicio de Grafana al puerto 3000 de la máquina:

    kubectl -n monitoring port-forward svc/prometheus-grafana 3000:http-web

Abrir otra pestaña en la terminal y realizar un port-forward del servicio de Prometheus al puerto 9090 de la máquina:

    kubectl -n monitoring port-forward svc/prometheus-kube-prometheus-prometheus 9090:9090

Acceder a la dirección http://localhost:3000 en el navegador para acceder a Grafana, las credenciales por defecto son admin para el usuario y prom-operator para la contraseña. Acceder a la dirección http://localhost:9090 para acceder al Prometheus, por defecto no se necesita autenticación.
Para acceder a nuestra aplicación usamos la dirección http://localhost:8081.

## Objetivo

El objetivo es mejorar un proyecto creado previamente para ponerlo en producción, a través de la adicción de una serie de mejoras.

## Proyecto inicial

El proyecto inicial es un servidor que realiza lo siguiente:

- Utiliza [FastAPI](https://fastapi.tiangolo.com/) para levantar un servidor en el puerto `8081` e implementa inicialmente dos endpoints:
  - `/`: Devuelve en formato `JSON` como respuesta `{"health": "ok"}` y un status code 200.
  - `/health`: Devuelve en formato `JSON` como respuesta `{"message":"Hello World"}` y un status code 200.

- Se han implementado tests unitarios para el servidor [FastAPI](https://fastapi.tiangolo.com/)

- Utiliza [prometheus-client](https://github.com/prometheus/client_python) para arrancar un servidor de métricas en el puerto `8000` y poder registrar métricas, siendo inicialmente las siguientes:
  - `Counter('server_requests_total', 'Total number of requests to this webserver')`: Contador que se incrementará cada vez que se haga una llamada a alguno de los endpoints implementados por el servidor (inicialmente `/` y `/health`)
  - `Counter('healthcheck_requests_total', 'Total number of requests to healthcheck')`: Contador que se incrementará cada vez que se haga una llamada al endpoint `/health`.
  - `Counter('main_requests_total', 'Total number of requests to main endpoint')`: Contador que se incrementará cada vez que se haga una llamada al endpoint `/`.

## Software necesario

Es necesario disponer del siguiente software:

- `Python` en versión `3.8.5` o superior, disponible para los diferentes sistemas operativos en la [página oficial de descargas](https://www.python.org/downloads/release/python-385/)

- `virtualenv` para poder instalar las librerías necesarias de Python, se puede instalar a través del siguiente comando:

    ```sh
    pip3 install virtualenv
    ```

    En caso de estar utilizando Linux y el comando anterior diera fallos se debe ejecutar el siguiente comando:

    ```sh
    sudo apt-get update && sudo apt-get install -y python3.8-venv
    ```

- `Docker` para poder arrancar el servidor implementado a través de un contenedor Docker, es posible descargarlo a [través de su página oficial](https://docs.docker.com/get-docker/).

## Ejecución de servidor

### Ejecución directa con Python

1. Instalación de un virtualenv, **realizarlo sólo en caso de no haberlo realizado previamente**:
   1. Obtener la versión actual de Python instalada para crear posteriormente un virtualenv:

        ```sh
        python3 --version
        ```

        El comando anterior mostrará algo como lo mostrado a continuación:ç

        ```sh
            Python 3.8.13
        ```

   2. Crear de virtualenv en la raíz del directorio para poder instalar las librerías necesarias:

       - En caso de en el comando anterior haber obtenido `Python 3.8.*`

            ```sh
            python3.8 -m venv venv
            ```

       - En caso de en el comando anterior haber obtenido `Python 3.9.*`:

           ```sh
           python3.9 -m venv venv
           ```

2. Activar el virtualenv creado en el directorio `venv` en el paso anterior:

     ```sh
     source venv/bin/activate
     ```

3. Instalar las librerías necesarias de Python, recogidas en el fichero `requirements.txt`, **sólo en caso de no haber realizado este paso previamente**. Es posible instalarlas a través del siguiente comando:

    ```sh
    pip3 install -r requirements.txt
    ```

4. Ejecución del código para arrancar el servidor:

    ```sh
    python3 src/app.py
    ```

5. La ejecución del comando anterior debería mostrar algo como lo siguiente:

    ```sh
    [2022-04-16 09:44:22 +0000] [1] [INFO] Running on http://0.0.0.0:8081 (CTRL + C to quit)
    ```

### Ejecución a través de un contenedor Docker

1. Crear una imagen Docker con el código necesario para arrancar el servidor:

    ```sh
    docker build -t simple-server:0.0.1 .
    ```

2. Arrancar la imagen construida en el paso anterior mapeando los puertos utilizados por el servidor de FastAPI y el cliente de prometheus:

    ```sh
    docker run -d -p 8000:8000 -p 8081:8081 --name simple-server simple-server:0.0.1
    ```

3. Obtener los logs del contenedor creado en el paso anterior:

    ```sh
    docker logs -f simple-server
    ```

4. La ejecución del comando anterior debería mostrar algo como lo siguiente:

    ```sh
    [2022-04-16 09:44:22 +0000] [1] [INFO] Running on http://0.0.0.0:8081 (CTRL + C to quit)
    ```

## Comprobación de endpoints de servidor y métricas

Una vez arrancado el servidor, utilizando cualquier de las formas expuestas en los apartados anteriores, es posible probar las funcionalidades implementadas por el servidor:

- Comprobación de servidor FastAPI, a través de llamadas a los diferentes endpoints:

  - Realizar una petición al endpoint `/`

      ```sh
      curl -X 'GET' \
      'http://0.0.0.0:8081/' \
      -H 'accept: application/json'
      ```

      Debería devolver la siguiente respuesta:

      ```json
      {"message":"Hello World"}
      ```

  - Realizar una petición al endpoint `/health`

      ```sh
      curl -X 'GET' \
      'http://0.0.0.0:8081/health' \
      -H 'accept: application/json' -v
      ```

      Debería devolver la siguiente respuesta.

      ```json
      {"health": "ok"}
      ```

- Comprobación de registro de métricas, si se accede a la URL `http://0.0.0.0:8000` se podrán ver todas las métricas con los valores actuales en ese momento:

  - Realizar varias llamadas al endpoint `/` y ver como el contador utilizado para registrar las llamadas a ese endpoint, `main_requests_total` ha aumentado, se debería ver algo como lo mostrado a continuación:

    ```sh
    # TYPE main_requests_total counter
    main_requests_total 4.0
    ```

  - Realizar varias llamadas al endpoint `/health` y ver como el contador utilizado para registrar las llamadas a ese endpoint, `healthcheck_requests_total` ha aumentado, se debería ver algo como lo mostrado a continuación:

    ```sh
    # TYPE healthcheck_requests_total counter
    healthcheck_requests_total 26.0
    ```

  - También se ha credo un contador para el número total de llamadas al servidor `server_requests_total`, por lo que este valor debería ser la suma de los dos anteriores, tal y como se puede ver a continuación:

    ```sh
    # TYPE server_requests_total counter
    server_requests_total 30.0
    ```

## Tests

Se ha implementado tests unitarios para probar el servidor FastAPI, estos están disponibles en el archivo `src/tests/app_test.py`.

Es posible ejecutar los tests de diferentes formas:

- Ejecución de todos los tests:

    ```sh
    pytest
    ```

- Ejecución de todos los tests y mostrar cobertura:

    ```sh
    pytest --cov
    ```

- Ejecución de todos los tests y generación de report de cobertura:

    ```sh
    pytest --cov --cov-report=html
    ```

## Practica a realizar

A partir del ejemplo inicial descrito en los apartados anteriores es necesario realizar una serie de mejoras:

Los requirimientos son los siguientes:

- Añadir por lo menos un nuevo endpoint a los existentes `/` y `/health`, un ejemplo sería `/bye` que devolvería `{"msg": "Bye Bye"}`, para ello será necesario añadirlo en el fichero [src/application/app.py](./src/application/app.py)

- Creación de tests unitarios para el nuevo endpoint añadido, para ello será necesario modificar el [fichero de tests](./src/tests/app_test.py)

- Opcionalmente creación de helm chart para desplegar la aplicación en Kubernetes, se dispone de un ejemplo de ello en el laboratorio realizado en la clase 3

- Creación de pipelines de CI/CD en cualquier plataforma (Github Actions, Jenkins, etc) que cuenten por lo menos con las siguientes fases:

  - Testing: tests unitarios con cobertura. Se dispone de un [ejemplo con Github Actions en el repositorio actual](./.github/workflows/test.yaml)

  - Build & Push: creación de imagen docker y push de la misma a cualquier registry válido que utilice alguna estrategia de release para los tags de las vistas en clase, se recomienda GHCR ya incluido en los repositorios de Github. Se dispone de un [ejemplo con Github Actions en el repositorio actual](./.github/workflows/release.yaml)

- Configuración de monitorización y alertas:

  - Configurar monitorización mediante prometheus en los nuevos endpoints añadidos, por lo menos con la siguiente configuración:
    - Contador cada vez que se pasa por el/los nuevo/s endpoint/s, tal y como se ha realizado para los endpoints implementados inicialmente

  - Desplegar prometheus a través de Kubernetes mediante minikube y configurar alert-manager para por lo menos las siguientes alarmas, tal y como se ha realizado en el laboratorio del día 3 mediante el chart `kube-prometheus-stack`:
    - Uso de CPU de un contenedor mayor al del límite configurado, se puede utilizar como base el ejemplo utilizado en el laboratorio 3 para mandar alarmas cuando el contenedor de la aplicación `fast-api` consumía más del asignado mediante request

  - Las alarmas configuradas deberán tener severity high o critical

  - Crear canal en slack `<nombreAlumno>-prometheus-alarms` y configurar webhook entrante para envío de alertas con alert manager

  - Alert manager estará configurado para lo siguiente:
    - Mandar un mensaje a Slack en el canal configurado en el paso anterior con las alertas con label "severity" y "critical"
    - Deberán enviarse tanto alarmas como recuperación de las mismas
    - Habrá una plantilla configurada para el envío de alarmas

    Para poder comprobar si esta parte funciona se recomienda realizar una prueba de estres, como la realizada en el laboratorio 3 a partir del paso 8.

  - Creación de un dashboard de Grafana, con por lo menos lo siguiente:
    - Número de llamadas a los endpoints
    - Número de veces que la aplicación ha arrancado

## Entregables

Se deberá entregar mediante un repositorio realizado a partir del original lo siguiente:

- Código de la aplicación y los tests modificados
- Ficheros para CI/CD configurados y ejemplos de ejecución válidos
- Ficheros para despliegue y configuración de prometheus de todo lo relacionado con este, así como el dashboard creado exportado a `JSON` para poder reproducirlo
- `README.md` donde se explique como se ha abordado cada uno de los puntos requeridos en el apartado anterior, con ejemplos prácticos y guía para poder reproducir cada uno de ellos
