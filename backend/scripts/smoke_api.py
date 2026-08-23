"""End-to-end API smoke check; uses disposable records and no delivery addresses."""
import sys
from datetime import datetime, timezone
from uuid import uuid4

import httpx


base_url = (sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000").rstrip("/")
results: list[tuple[str, int]] = []


def check(client: httpx.Client, method: str, path: str, expected=(200,), **kwargs):
    response = client.request(method, path, **kwargs)
    results.append((f"{method} {path}", response.status_code))
    if response.status_code not in expected:
        raise RuntimeError(f"{method} {path}: expected {expected}, got {response.status_code}: {response.text[:300]}")
    return response


with httpx.Client(base_url=base_url, timeout=20, follow_redirects=True) as client:
    check(client, "GET", "/health")
    check(client, "GET", "/ready")
    check(client, "GET", "/openapi.json")
    check(client, "GET", "/agents")
    check(client, "GET", "/analytics/impact")
    check(client, "GET", "/incidents")
    check(client, "GET", "/incidents/patterns")

    email = f"smoke-{uuid4()}@example.com"
    password = "SmokeTestPassword42"
    check(client, "POST", "/auth/register", (201,), json={"preferred_name": "API smoke test", "email": email, "password": password, "confirm_password": password, "accept_terms": True})
    csrf = client.cookies.get("shakti_csrf")
    headers = {"X-CSRF-Token": csrf}
    check(client, "GET", "/auth/me")
    check(client, "POST", "/auth/refresh", headers=headers, json={})
    check(client, "POST", "/auth/forgot-password", (202,), json={"email": email})

    journey = check(client, "POST", "/journeys", json={"origin": "Smoke origin", "destination": "Smoke destination", "eta_minutes": 10, "battery_percent": 70}).json()
    journey_id = journey["id"]
    check(client, "GET", f"/journeys/{journey_id}")
    check(client, "POST", f"/journeys/{journey_id}/sos", json={})
    check(client, "POST", "/journeys/safeword", json={"journey_id": journey_id, "phrase": "blue notebook"})
    check(client, "POST", "/journeys/checkin", json={"journey_id": journey_id, "user_safe": True})

    check(client, "POST", "/resources/nearby", json={"latitude": 32.95, "longitude": -97.22, "radius_km": 5})
    check(client, "POST", "/resources/nearby-v2", json={"latitude": 32.95, "longitude": -97.22, "radius_km": 5})
    check(client, "POST", "/agents/cyber", json={"text": "Urgent: verify your bank account at example.test"})
    check(client, "POST", "/agents/privacy", json={"active_journey": False, "location_permission": "while_using", "notification_preview_enabled": False, "evidence_encrypted": True, "app_lock_enabled": True})
    check(client, "POST", "/agents/context", json={"active_journey": True, "battery_percent": 70})
    check(client, "POST", "/readiness", json={"trusted_contacts_count": 1, "location_always_on": False, "emergency_plan_configured": True, "app_lock_enabled": True, "notification_privacy_enabled": True, "account_security_reviewed": True})
    check(client, "POST", "/battery/policy", json={"battery_level": 70, "journey_state": "active"})
    check(client, "POST", "/incidents", json={"title": "API smoke record", "description": "Disposable operational check", "occurred_at": datetime.now(timezone.utc).isoformat(), "tags": ["smoke-test"]})
    check(client, "POST", "/feedback", json={"rating": 5, "useful": True, "text": "API smoke test"})

    check(client, "GET", "/notifications/status")
    check(client, "GET", "/guardians")
    guardian = check(client, "POST", "/guardians", json={"name": "Smoke guardian", "relationship": "test"}, headers=headers).json()
    guardian_id = guardian["id"]
    check(client, "GET", f"/guardian-invites/{guardian['invite_token']}")
    check(client, "POST", f"/guardians/{guardian_id}/send-invite", json={"channels": ["sms"]}, headers=headers)
    check(client, "POST", "/guardians/notify", json={"event": "journey_started", "journey_id": journey_id}, headers=headers)
    sos = check(client, "POST", "/sos", json={"journey_id": journey_id, "battery_percent": 70}, headers=headers).json()
    check(client, "POST", f"/sos/{sos['id']}/cancel", json={"reason": "smoke_test"}, headers=headers)
    check(client, "DELETE", f"/guardians/{guardian_id}", headers=headers)

    check(client, "POST", "/auth/logout", headers=headers, json={})
    check(client, "POST", "/auth/login", json={"email": email, "password": password})

for operation, status in results:
    print(f"PASS {status} {operation}")
print(f"PASS: {len(results)} production operations")
