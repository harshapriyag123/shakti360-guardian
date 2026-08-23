from fastapi.testclient import TestClient
from uuid import uuid4
from app.main import app, guardians, sos_sessions

client = TestClient(app)

def setup_function():
    guardians.clear()
    sos_sessions.clear()

def signed_in_client():
    session = TestClient(app)
    response = session.post("/auth/register", json={"preferred_name": "Guardian owner", "email": f"guardian-{uuid4()}@example.com", "password": "StrongPassword123", "confirm_password": "StrongPassword123", "accept_terms": True})
    assert response.status_code == 201
    session.headers["X-CSRF-Token"] = session.cookies.get("shakti_csrf")
    return session

def test_guardian_invite_has_expiry_and_permissions():
    session = signed_in_client()
    created = session.post("/guardians", json={"name": "Asha", "relationship": "friend"}).json()
    assert created["invite_expires_at"]
    invite = client.get(f"/guardian-invites/{created['invite_token']}")
    assert invite.status_code == 200
    assert invite.json()["permissions"]["live_location"] is True

def test_delivery_requires_authentication():
    assert client.post("/guardians/not-real/send-invite", json={"channels": ["sms"]}).status_code == 401

def test_unconfigured_delivery_is_reported_truthfully():
    session = signed_in_client()
    guardian = session.post("/guardians", json={"name": "Asha", "phone": "+15551234567", "email": "asha@example.com"}).json()
    response = session.post(f"/guardians/{guardian['id']}/send-invite", json={"channels": ["sms", "email"]})
    assert response.status_code == 200
    assert {result["status"] for result in response.json()["deliveries"]} == {"not_configured"}

def test_phone_requires_international_format():
    session = signed_in_client()
    assert session.post("/guardians", json={"name": "Asha", "phone": "555-1234"}).status_code == 422

def test_missing_guardian_invite_is_rejected():
    assert client.get("/guardian-invites/not-a-token").status_code == 404

def test_sos_never_claims_emergency_services_contacted():
    response = signed_in_client().post("/sos", json={"battery_percent": 42})
    assert response.status_code == 200
    assert response.json()["emergency_services_contacted"] is False

def test_sos_can_be_cancelled_by_user():
    client_session = signed_in_client()
    session = client_session.post("/sos", json={}).json()
    cancelled = client_session.post(f"/sos/{session['id']}/cancel", json={"reason": "user_safe"})
    assert cancelled.status_code == 200
    assert cancelled.json()["status"] == "cancelled"

def test_notification_status_never_exposes_credentials():
    response = signed_in_client().get("/notifications/status")
    assert response.status_code == 200
    assert set(response.json()["providers"]["sms"]) == {"provider", "configured"}

def test_guardian_alert_respects_selected_permission():
    session = signed_in_client()
    session.post("/guardians", json={"name": "Asha", "email": "asha@example.com", "journey_started": False, "sos": True})
    journey = session.post("/guardians/notify", json={"event": "journey_started"}).json()
    sos = session.post("/guardians/notify", json={"event": "sos"}).json()
    assert journey["recipient_count"] == 0
    assert sos["recipient_count"] == 1
