from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app, incidents


def setup_function():
    incidents.clear()


def signed_in_client(label: str):
    session = TestClient(app)
    response = session.post("/auth/register", json={
        "preferred_name": label,
        "email": f"{label.lower()}-{uuid4()}@example.com",
        "password": "StrongPassword123",
        "confirm_password": "StrongPassword123",
        "accept_terms": True,
    })
    assert response.status_code == 201
    session.headers["X-CSRF-Token"] = session.cookies.get("shakti_csrf")
    return session


def incident_payload(description: str):
    return {
        "title": "Unwanted contact",
        "description": description,
        "tags": ["digital", "unwanted-contact"],
    }


def test_evidence_endpoints_require_authentication():
    anonymous = TestClient(app)
    assert anonymous.post("/incidents", json=incident_payload("private details")).status_code == 401
    assert anonymous.get("/incidents").status_code == 401
    assert anonymous.get("/incidents/patterns").status_code == 401


def test_evidence_records_are_isolated_by_account():
    alice = signed_in_client("Alice")
    bob = signed_in_client("Bob")

    created = alice.post("/incidents", json=incident_payload("Alice-only details"))
    assert created.status_code == 200
    assert "owner_user_id" not in created.json()

    alice_records = alice.get("/incidents")
    bob_records = bob.get("/incidents")
    assert alice_records.status_code == bob_records.status_code == 200
    assert [record["description"] for record in alice_records.json()["incidents"]] == ["Alice-only details"]
    assert bob_records.json()["incidents"] == []

    assert alice.get("/incidents/patterns").json()["incident_count"] == 1
    assert bob.get("/incidents/patterns").json()["incident_count"] == 0


def test_saving_evidence_requires_csrf():
    session = signed_in_client("NoCsrf")
    session.headers.pop("X-CSRF-Token")
    assert session.post("/incidents", json=incident_payload("blocked")).status_code == 403
