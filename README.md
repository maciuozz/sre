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

A continuación hay algunas capturas de las fases de test y release:

<img width="1789" alt="Screenshot 2023-04-26 at 00 00 05" src="https://user-images.githubusercontent.com/118285718/234414697-e3255e4c-5a39-461b-9d0f-4226f08cae51.png">
<img width="1791" alt="Screenshot 2023-04-26 at 00 00 35" src="https://user-images.githubusercontent.com/118285718/234414711-e3f166c5-d143-443d-be98-4c826e313be7.png">
<img width="1792" alt="Screenshot 2023-04-26 at 00 01 04" src="https://user-images.githubusercontent.com/118285718/234414728-9dee4ee5-fb74-4db6-b55e-77ce499aebf4.png">

Aqui se pueden observar las imagenes subidas a GitHub Container Registry y a Docker Hub:

<img width="1790" alt="Screenshot 2023-04-26 at 00 08 08" src="https://user-images.githubusercontent.com/118285718/234415976-4f122de1-ba2d-4951-87e1-6137d9e656c3.png">
<img width="1792" alt="Screenshot 2023-04-26 at 00 08 53" src="https://user-images.githubusercontent.com/118285718/234415987-b1940f14-07e9-42ab-875a-bc0de5f9ad15.png">

Para desplegar Prometheus creamos un cluster de Kubernetes que utilice la versión v1.21.1 utilizando minikube para ello a través de un nuevo perfil llamado monitoring-demo:

    minikube start --kubernetes-version='v1.21.1' --memory=4096 --addons="metrics-server -p monitoring-demo

Añadir el repositorio de helm prometheus-community para poder desplegar el chart kube-prometheus-stack:

    helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
    helm repo update

Desplegar el chart kube-prometheus-stack del repositorio de helm añadido en el paso anterior con los valores configurados en el archivo kube-prometheus-stack/values.yaml en el namespace monitoring:

    helm -n monitoring upgrade --install prometheus prometheus-community/kube-prometheus-stack -f kube-prometheus-stack/values.yaml --create-namespace --wait --version 34.1.1
    
En el archivo ***values.yaml*** se establece la configuración para conectar Prometheus con Slack. Para ver los pod en el namespace monitoring utilizado para desplegar el stack de prometheus: 

    kubectl -n monitoring get po -w

Desplegamos nuestra aplicación que utiliza [FastAPI](https://fastapi.tiangolo.com/) para levantar un servidor en el puerto 8081 en el mismo 
namespace, utilizando Helm:

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

<img width="1382" alt="Screenshot 2023-04-25 at 23 41 36" src="https://user-images.githubusercontent.com/118285718/234411323-c20acfc6-c5b2-44e1-86fd-f99ff771f6c9.png">
<img width="1390" alt="Screenshot 2023-04-25 at 23 43 09" src="https://user-images.githubusercontent.com/118285718/234411385-83dab2a4-cdce-4ea9-b451-b12ef61b950b.png">
<img width="1347" alt="Screenshot 2023-04-25 at 23 43 31" src="https://user-images.githubusercontent.com/118285718/234411439-b9b3d80f-21d4-4c81-bd3f-cc101bc014a0.png">

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
    
Como que hemos configurado prometheus para que nos avise si la tasa promedio de uso de CPU es mayor que la cantidad promedio de CPU solicitada por el contenedor, despues de unos minutos deberíamos recibir notificaciones en Slack:

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

Abriendo http://localhost:8000/ vemos:

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






