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

def test_health_disables_caching_and_has_request_id():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    assert response.headers["x-request-id"]

def test_pwa_localhost_origin_is_allowed():
    response = client.get("/health", headers={"Origin": "http://localhost:8080"})
    assert response.headers["access-control-allow-origin"] == "http://localhost:8080"

def test_pwa_loopback_origin_is_allowed():
    response = client.get("/health", headers={"Origin": "http://127.0.0.1:8080"})
    assert response.headers["access-control-allow-origin"] == "http://127.0.0.1:8080"

def test_dynamic_expo_development_port_is_allowed():
    response = client.get("/health", headers={"Origin": "http://localhost:9876"})
    assert response.headers["access-control-allow-origin"] == "http://localhost:9876"

def test_nearby_rejects_invalid_latitude():
    response = client.post("/resources/nearby", json={"latitude": 91, "longitude": 0, "radius_km": 5})
    assert response.status_code == 422

def test_nearby_rejects_excessive_radius():
    response = client.post("/resources/nearby", json={"latitude": 0, "longitude": 0, "radius_km": 100})
    assert response.status_code == 422

def test_battery_policy_validates_percentage():
    response = client.post("/battery/policy", json={"battery_level": 101, "journey_state": "active"})
    assert response.status_code == 422

def test_battery_policy_rejects_unknown_journey_state():
    response = client.post("/battery/policy", json={"battery_level": 80, "journey_state": "danger"})
    assert response.status_code == 422

def test_battery_policy_endpoint_stops_completed_tracking():
    response = client.post("/battery/policy", json={"battery_level": 80, "journey_state": "completed"})
    assert response.status_code == 200
    assert response.json()["tracking_enabled"] is False

def test_guardian_can_be_removed():
    session = signed_in_client()
    guardian = session.post("/guardians", json={"name": "Maya"}).json()
    assert session.delete(f"/guardians/{guardian['id']}").status_code == 200
    assert session.get("/guardians").json()["guardians"] == []

def test_missing_guardian_delete_returns_404():
    assert signed_in_client().delete("/guardians/missing").status_code == 404

def test_missing_sos_cancel_returns_404():
    assert signed_in_client().post("/sos/missing/cancel", json={"reason": "user_safe"}).status_code == 404
