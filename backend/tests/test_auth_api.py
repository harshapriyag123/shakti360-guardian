from uuid import uuid4
from fastapi.testclient import TestClient
from sqlalchemy import select
from app.main import app
from app.auth_models import RefreshSession, User
from app.database import SessionLocal

client = TestClient(app)
PASSWORD = "StrongPassword42"

def payload(**overrides):
    data = {"preferred_name": "Maya", "email": f"maya-{uuid4()}@example.com", "password": PASSWORD, "confirm_password": PASSWORD, "accept_terms": True}
    data.update(overrides); return data

def register(**overrides): return client.post("/auth/register", json=payload(**overrides))

def test_register_persists_normalized_user():
    email = f"CASE-{uuid4()}@Example.COM"
    response = register(email=email)
    assert response.status_code == 201
    assert response.json()["user"]["email"] == email.lower()

def test_password_is_argon2_hashed_not_plaintext():
    email = f"hash-{uuid4()}@example.com"
    assert register(email=email).status_code == 201
    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.email == email))
        assert user and user.password_hash.startswith("$argon2")
        assert PASSWORD not in user.password_hash

def test_register_sets_httponly_session_cookies():
    response = register()
    cookies = response.headers.get_list("set-cookie")
    assert any("shakti_access=" in value and "HttpOnly" in value for value in cookies)
    assert any("shakti_refresh=" in value and "HttpOnly" in value for value in cookies)
    assert any("shakti_csrf=" in value and "HttpOnly" not in value for value in cookies)

def test_refresh_cookie_is_available_through_production_api_proxy():
    response = register()
    refresh_cookie = next(value for value in response.headers.get_list("set-cookie") if value.startswith("shakti_refresh="))
    assert "Path=/" in refresh_cookie
    assert "Path=/auth" not in refresh_cookie

def test_duplicate_email_is_rejected():
    email = f"duplicate-{uuid4()}@example.com"
    assert register(email=email).status_code == 201
    assert register(email=email.upper()).status_code == 409

def test_registration_requires_terms_consent():
    assert register(accept_terms=False).status_code == 422

def test_registration_rejects_password_mismatch():
    assert register(confirm_password="DifferentPassword42").status_code == 422

def test_registration_rejects_weak_password():
    assert register(password="alllowercase12", confirm_password="alllowercase12").status_code == 422

def test_me_requires_authentication():
    assert TestClient(app).get("/auth/me").status_code == 401

def test_registered_session_can_read_me():
    session = TestClient(app); created = session.post("/auth/register", json=payload())
    me = session.get("/auth/me")
    assert created.status_code == 201 and me.status_code == 200
    assert me.json()["user"]["id"] == created.json()["user"]["id"]

def test_login_uses_human_friendly_generic_error():
    response = client.post("/auth/login", json={"email": f"missing-{uuid4()}@example.com", "password": "wrong"})
    assert response.status_code == 401
    assert "doesn't match our records" in response.json()["detail"]

def test_login_succeeds_with_correct_password():
    email = f"login-{uuid4()}@example.com"; register(email=email)
    response = TestClient(app).post("/auth/login", json={"email": email, "password": PASSWORD, "remember_me": True})
    assert response.status_code == 200
    assert response.json()["user"]["email"] == email

def test_account_locks_after_five_failed_attempts():
    email = f"lock-{uuid4()}@example.com"; register(email=email)
    session = TestClient(app)
    for _ in range(5): assert session.post("/auth/login", json={"email": email, "password": "wrong"}).status_code == 401
    assert session.post("/auth/login", json={"email": email, "password": PASSWORD}).status_code == 429

def test_refresh_requires_csrf_header():
    session = TestClient(app); session.post("/auth/register", json=payload())
    assert session.post("/auth/refresh").status_code == 403

def test_refresh_accepts_matching_csrf():
    session = TestClient(app); session.post("/auth/register", json=payload())
    csrf = session.cookies.get("shakti_csrf")
    assert session.post("/auth/refresh", headers={"X-CSRF-Token": csrf}).status_code == 200

def test_logout_revokes_refresh_session():
    session = TestClient(app); created = session.post("/auth/register", json=payload())
    csrf = session.cookies.get("shakti_csrf"); user_id = created.json()["user"]["id"]
    assert session.post("/auth/logout", headers={"X-CSRF-Token": csrf}).status_code == 200
    with SessionLocal() as db:
        stored = db.scalars(select(RefreshSession).where(RefreshSession.user_id == user_id)).all()
        assert stored and all(item.revoked for item in stored)

def test_forgot_password_does_not_reveal_account_existence():
    missing = client.post("/auth/forgot-password", json={"email": f"missing-{uuid4()}@example.com"})
    existing_email = f"forgot-{uuid4()}@example.com"; register(email=existing_email)
    existing = client.post("/auth/forgot-password", json={"email": existing_email})
    assert missing.status_code == existing.status_code == 202
    assert missing.json() == existing.json()

def test_ready_reports_database_available():
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json()["database"] == "available"
