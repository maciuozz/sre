"""
This module  defines a FastAPI application with 4 endpoints. The FastAPI() function is called to create
a new instance of the FastAPI application. The SimpleServer class is defined with a run_server() method that
uses the Hypercorn 'serve' function to start the server with the specified configuration parameters.
Hypercorn server is being used to serve the FastAPI application that listens on port 8081.
"""

from fastapi import FastAPI
from hypercorn.asyncio import serve
from hypercorn.config import Config as HyperCornConfig
from prometheus_client import Counter
import requests

app = FastAPI()

REQUESTS = Counter('server_requests_total', 'Total number of requests to this webserver')
HEALTHCHECK_REQUESTS = Counter('healthcheck_requests_total', 'Total number of requests to healthcheck')
MAIN_ENDPOINT_REQUESTS = Counter('main_requests_total', 'Total number of requests to main endpoint')

############################################### ADDITIONAL COUNTERS ################################################
#We create 3 counters for the 2 additional endpoints and the other one to
#count the number of times the application has started.
#The endpoint counters are used to collect metrics on the total number of requests received by each of these endpoints.
BYE_ENDPOINT_REQUESTS = Counter('bye_requests_total', 'Total number of requests to bye endpoint')
JOKE_ENDPOINT_REQUESTS = Counter('joke_requests_total', 'Total number of requests to joke endpoint')
APP_START_COUNT = Counter('app_start_count', 'Number of times the application has started')


class SimpleServer:
    """
    SimpleServer class define FastAPI configuration and implemented endpoints
    """

    _hypercorn_config = None

    def __init__(self):
        self._hypercorn_config = HyperCornConfig()

    async def run_server(self):
        """Starts the server with the config parameters"""
        self._hypercorn_config.bind = ['0.0.0.0:8081']
        self._hypercorn_config.keep_alive_timeout = 90
        #Keep count of the number of times the application has started.
        APP_START_COUNT.inc()
        await serve(app, self._hypercorn_config)

    @staticmethod
    @app.get("/health")
    async def health_check():
        """Implement health check endpoint"""
        #Increase the counter used to record the overall number of requests made to the webserver.
        REQUESTS.inc()
        #Increase the counter used to record the requests made to the health check endpoint.
        HEALTHCHECK_REQUESTS.inc()
        return {"health": "ok"}

    @staticmethod
    @app.get("/")
    async def read_main():
        """Implement main endpoint"""
        REQUESTS.inc()
        MAIN_ENDPOINT_REQUESTS.inc()
        return {"msg": "Hello World"}

###################################### ADDITIONAL ENDPOINTS #########################################

#Endpoint that returns the message "Bye Bye".
    @staticmethod
    @app.get("/bye")
    async def say_bye():
        """Implement bye endpoint"""
        REQUESTS.inc()
        BYE_ENDPOINT_REQUESTS.inc()
        return {"msg": "Bye Bye"}

#Endpoint that uses the 'requests' library to get a random joke from an external API.
#If the request to get the joke is unsuccessful, the
#function returns an error message. If it is successful, it returns the joke in JSON format.
    @staticmethod
    @app.get("/joke")
    async def tell_joke():
        """Tell a joke"""
        REQUESTS.inc()
        JOKE_ENDPOINT_REQUESTS.inc()

        #Use requests library to get a random joke from an API.
        url = "https://official-joke-api.appspot.com/random_joke"
        response = requests.get(url)
        if response.status_code != 200:
            return {"error": "Failed to get a joke"}

        joke = response.json()
        return {"setup": joke["setup"], "punchline": joke["punchline"]}
