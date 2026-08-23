import hashlib, os, secrets
from datetime import datetime, timedelta, timezone
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError
import jwt

JWT_SECRET = os.getenv("JWT_SECRET", "development-only-change-me")
if os.getenv("APP_ENV") == "production" and JWT_SECRET == "development-only-change-me":
    raise RuntimeError("JWT_SECRET must be configured in production")
JWT_ALGORITHM = "HS256"
ACCESS_MINUTES = 15
ph = PasswordHasher(time_cost=2, memory_cost=19456, parallelism=1)

def hash_password(password: str) -> str: return ph.hash(password)
def verify_password(password_hash: str, password: str) -> bool:
    try: return ph.verify(password_hash, password)
    except (VerifyMismatchError, InvalidHashError): return False
def create_access_token(user_id: str) -> str:
    now = datetime.now(timezone.utc)
    return jwt.encode({"sub": user_id, "type": "access", "iat": now, "exp": now + timedelta(minutes=ACCESS_MINUTES)}, JWT_SECRET, algorithm=JWT_ALGORITHM)
def decode_access_token(token: str) -> str:
    payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    if payload.get("type") != "access" or not payload.get("sub"): raise jwt.InvalidTokenError()
    return str(payload["sub"])
def new_refresh_token() -> str: return secrets.token_urlsafe(48)
def token_hash(token: str) -> str: return hashlib.sha256(token.encode()).hexdigest()
