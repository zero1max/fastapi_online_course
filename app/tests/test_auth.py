import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@pytest.mark.asyncio
async def test_register():
    response = client.post("/auth/register", json={
        "full_name": "Test User",
        "email": "test@example.com",
        "password": "testpassword"
    })
    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"

@pytest.mark.asyncio
async def test_login():
    response = client.post("/auth/login", data={
        "username": "test@example.com",
        "password": "testpassword"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()