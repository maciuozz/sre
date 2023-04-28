"""
Module used for testing simple server module
"""

from fastapi.testclient import TestClient
import pytest
import httpx

from application.app import app



client = TestClient(app)

class TestSimpleServer:
    """
    TestSimpleServer class for testing SimpleServer
    """
    @pytest.mark.asyncio
    async def read_health_test(self):
        """Tests the health check endpoint"""
        response = client.get("health")

        assert response.status_code == 200
        assert response.json() == {"health": "ok"}

    @pytest.mark.asyncio
    async def read_main_test(self):
        """Tests the main endpoint"""
        response = client.get("/")

        assert response.status_code == 200
        assert response.json() == {"msg": "Hello World"}

######################################## ADDITIONAL TESTS ##########################################

#The 'bye_bye_test' function tests the '/bye' endpoint by making a GET request
#to it and checking that the HTTP status code is 200 and the response JSON contains the message "Bye Bye".
    @pytest.mark.asyncio
    async def bye_bye_test(self):
        """Tests the bye endpoint"""
        response = client.get("bye")

        assert response.status_code == 200
        assert response.json() == {"msg": "Bye Bye"}

#The 'joke_endpoint_test' function tests the '/joke' endpoint by making an asynchronous GET request to it
#using the httpx.AsyncClient and checking that the HTTP status code is 200 and the response JSON contains
#the expected fields "setup" and "punchline", which are both strings with a length greater than zero.
    @pytest.mark.asyncio
    async def joke_endpoint_test(self):
        """Tests the joke endpoint"""
        async with httpx.AsyncClient(app=app, base_url="http://test") as async_client:
            response = await async_client.get("/joke")
        assert response.status_code == 200
        data = response.json()
        assert "setup" in data
        assert isinstance(data["setup"], str)
        assert "punchline" in data
        assert isinstance(data["punchline"], str)
        assert len(data["setup"]) > 0
        assert len(data["punchline"]) > 0
