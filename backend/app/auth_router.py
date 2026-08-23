import os, secrets
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Cookie, Depends, Header, HTTPException, Request, Response
from pydantic import BaseModel, EmailStr, Field, model_validator
from sqlalchemy import select
from sqlalchemy.orm import Session
import jwt
from .auth import create_access_token, decode_access_token, hash_password, new_refresh_token, token_hash, verify_password
from .auth_models import RefreshSession, User
from .database import get_db

router = APIRouter(prefix="/auth", tags=["authentication"])
COOKIE_SECURE = os.getenv("APP_ENV", "dev") == "production"

class RegisterRequest(BaseModel):
    preferred_name: str = Field(min_length=1, max_length=80)
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)
    confirm_password: str
    age_group: str | None = Field(default=None, max_length=30)
    accept_terms: bool
    @model_validator(mode="after")
    def validate_registration(self):
        if self.password != self.confirm_password: raise ValueError("Passwords do not match")
        if not self.accept_terms: raise ValueError("Terms and Privacy Policy consent is required")
        if not any(c.isupper() for c in self.password) or not any(c.islower() for c in self.password) or not any(c.isdigit() for c in self.password): raise ValueError("Password must include uppercase, lowercase, and a number")
        return self

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)
    remember_me: bool = False

def public_user(user: User): return {"id": user.id, "email": user.email, "preferred_name": user.preferred_name, "age_group": user.age_group, "email_verified": user.email_verified, "created_at": user.created_at}

def issue_session(response: Response, db: Session, user: User, remember: bool = False):
    refresh = new_refresh_token(); csrf = secrets.token_urlsafe(24); days = 30 if remember else 7
    db.add(RefreshSession(user_id=user.id, token_hash=token_hash(refresh), csrf_token=csrf, expires_at=datetime.now(timezone.utc) + timedelta(days=days))); db.commit()
    response.set_cookie("shakti_access", create_access_token(user.id), httponly=True, secure=COOKIE_SECURE, samesite="lax", max_age=900, path="/")
    # Production exposes this route as /api/auth/* through Nginx, so the
    # refresh cookie must be valid for both direct and proxied API paths.
    response.set_cookie("shakti_refresh", refresh, httponly=True, secure=COOKIE_SECURE, samesite="strict", max_age=days * 86400, path="/")
    response.set_cookie("shakti_csrf", csrf, httponly=False, secure=COOKIE_SECURE, samesite="strict", max_age=days * 86400, path="/")

@router.post("/register", status_code=201)
def register(req: RegisterRequest, response: Response, db: Session = Depends(get_db)):
    email = req.email.lower()
    if db.scalar(select(User).where(User.email == email)): raise HTTPException(409, "An account with this email already exists.")
    user = User(email=email, preferred_name=req.preferred_name.strip(), password_hash=hash_password(req.password), age_group=req.age_group, terms_accepted_at=datetime.now(timezone.utc))
    db.add(user); db.commit(); db.refresh(user); issue_session(response, db, user)
    return {"user": public_user(user), "message": "Account created. Email verification delivery is not configured in hackathon mode."}

@router.post("/login")
def login(req: LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == req.email.lower()))
    generic = "The email or password you entered doesn't match our records."
    if not user: raise HTTPException(401, generic)
    now = datetime.now(timezone.utc)
    locked_until = user.locked_until
    if locked_until and locked_until.tzinfo is None: locked_until = locked_until.replace(tzinfo=timezone.utc)
    if locked_until and locked_until > now: raise HTTPException(429, "Too many attempts. Try again later.")
    if not verify_password(user.password_hash, req.password):
        user.failed_login_count += 1
        if user.failed_login_count >= 5: user.locked_until = now + timedelta(minutes=15); user.failed_login_count = 0
        db.commit(); raise HTTPException(401, generic)
    user.failed_login_count = 0; user.locked_until = None; db.commit(); issue_session(response, db, user, req.remember_me)
    return {"user": public_user(user)}

def require_csrf(csrf_cookie: str | None, csrf_header: str | None):
    if not csrf_cookie or not csrf_header or not secrets.compare_digest(csrf_cookie, csrf_header): raise HTTPException(403, "Security token missing or invalid. Refresh and try again.")

@router.post("/refresh")
def refresh(response: Response, db: Session = Depends(get_db), refresh_token: str | None = Cookie(None, alias="shakti_refresh"), csrf_cookie: str | None = Cookie(None, alias="shakti_csrf"), csrf_header: str | None = Header(None, alias="X-CSRF-Token")):
    require_csrf(csrf_cookie, csrf_header)
    if not refresh_token: raise HTTPException(401, "Session expired. Please sign in again.")
    session = db.scalar(select(RefreshSession).where(RefreshSession.token_hash == token_hash(refresh_token)))
    now = datetime.now(timezone.utc); expires = session.expires_at if session else None
    if expires and expires.tzinfo is None: expires = expires.replace(tzinfo=timezone.utc)
    if not session or session.revoked or not expires or expires <= now or not secrets.compare_digest(session.csrf_token, csrf_cookie or ""): raise HTTPException(401, "Session expired. Please sign in again.")
    response.set_cookie("shakti_access", create_access_token(session.user_id), httponly=True, secure=COOKIE_SECURE, samesite="lax", max_age=900, path="/")
    return {"status": "refreshed"}

@router.post("/logout")
def logout(response: Response, db: Session = Depends(get_db), refresh_token: str | None = Cookie(None, alias="shakti_refresh"), csrf_cookie: str | None = Cookie(None, alias="shakti_csrf"), csrf_header: str | None = Header(None, alias="X-CSRF-Token")):
    require_csrf(csrf_cookie, csrf_header)
    if refresh_token:
        session = db.scalar(select(RefreshSession).where(RefreshSession.token_hash == token_hash(refresh_token)))
        if session: session.revoked = True; db.commit()
    for name in ("shakti_access", "shakti_refresh", "shakti_csrf"): response.delete_cookie(name, path="/")
    return {"status": "signed_out"}

def current_user(request: Request, db: Session = Depends(get_db)) -> User:
    token = request.cookies.get("shakti_access")
    if not token: raise HTTPException(401, "Please sign in to continue.")
    try: user_id = decode_access_token(token)
    except jwt.PyJWTError: raise HTTPException(401, "Your session expired. Please sign in again.")
    user = db.get(User, user_id)
    if not user: raise HTTPException(401, "Your account could not be found.")
    return user

@router.get("/me")
def me(user: User = Depends(current_user)): return {"user": public_user(user)}

@router.post("/forgot-password", status_code=202)
def forgot_password(payload: dict):
    return {"message": "If an account exists, password-reset instructions will be sent. Email delivery is not configured in hackathon mode."}
