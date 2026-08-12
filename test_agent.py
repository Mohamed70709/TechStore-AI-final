from fastapi.testclient import TestClient

from api.main import app


client = TestClient(app)


def test_agent_workflow():
    response = client.post(
        "/chat",
        json={
            "session_id": "test_agent_workflow",
            "message": "What is your return policy?"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["reply"]
    assert len(data["reply"].strip()) > 0