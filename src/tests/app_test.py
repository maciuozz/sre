"""
Module used for testing simple server module
"""

from fastapi.testclient import TestClient
import pytest, httpx 

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
    
    @pytest.mark.asyncio
    async def bye_bye_test(self):
        """Tests the bye endpoint"""
        response = client.get("bye")

        assert response.status_code == 200
        assert response.json() == {"msg": "Bye Bye"}

    @pytest.mark.asyncio
    async def joke_endpoint_test(self):
        async with httpx.AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/joke")
        assert response.status_code == 200
        data = response.json()
        assert "setup" in data
        assert isinstance(data["setup"], str)
        assert "punchline" in data
        assert isinstance(data["punchline"], str)
        assert len(data["setup"]) > 0
        assert len(data["punchline"]) > 0
