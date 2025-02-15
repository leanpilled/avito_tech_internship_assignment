from fastapi.testclient import TestClient
from domain.entities.models import AuthRequest
from main import app

client = TestClient(app)

def test_auth():
    response = client.post(
        "/auth/",
        json=AuthRequest(
            username="a",
            password="a",
        ).model_dump()
    )
    assert response.status_code == 200
