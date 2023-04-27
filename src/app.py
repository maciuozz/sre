
"""
Module that launches an application that uses the Prometheus monitoring system to expose metrics over HTTP.
The module defines a Container class with a start_server() method that starts the application server.
The start_server() method launches an instance of the SimpleServer class defined in a module called app,
which contains the application code. In the if __name__ == "__main__": block, the start_http_server() function
from the prometheus_client module is called with an argument of 8000, which starts a Prometheus metrics endpoint on port 8000.
"""

import asyncio

from prometheus_client import start_http_server
from application.app import SimpleServer


class Container:
    """
    Class Container configure necessary methods to launch the application
    """

    def __init__(self):
        self._simple_server = SimpleServer()

    async def start_server(self):
        """Function for start server"""
        await self._simple_server.run_server()


if __name__ == "__main__":
    start_http_server(8000)
    container = Container()
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(container.start_server(), loop=loop)
    loop.run_forever()
