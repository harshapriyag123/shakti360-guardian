from fastapi import Cookie, Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta, timezone
from uuid import uuid4
import secrets
import os

from .models import (
    JourneyCreate, JourneyState, CheckinRequest, NearbyRequest,
    CyberRequest, IncidentCreate, PrivacyRequest, BatteryPolicyRequest
)
from .agents import (
    battery_guardian, escalation_engine, cyber_guardian,
    privacy_guardian, evidence_summarizer
)
from .resources import nearby
from .database import Base, engine
from . import auth_models  # registers SQLAlchemy tables
from .auth_router import current_user, require_csrf, router as auth_router
from .auth_models import User

app = FastAPI(
    title="Shakti360 Guardian API",
    version="0.1.0",
    description="Battery-aware agentic safety MVP"
)
Base.metadata.create_all(bind=engine)
app.include_router(auth_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in os.getenv("CORS_ORIGINS", "http://localhost:8080,http://localhost:8081,http://localhost:19006,http://localhost:8091,http://127.0.0.1:8080,http://127.0.0.1:8081,http://127.0.0.1:19006,http://127.0.0.1:8091").split(",") if origin.strip()],
    allow_origin_regex=None if os.getenv("APP_ENV") == "production" else r"^http://(localhost|127\.0\.0\.1|10(?:\.\d{1,3}){3}|192\.168(?:\.\d{1,3}){2}|172\.(?:1[6-9]|2\d|3[01])(?:\.\d{1,3}){2})(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Request-ID"] = str(uuid4())
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Cache-Control"] = "no-store"
    return response

journeys = {}
incidents = []
guardians = {}
sos_sessions = {}

@app.get("/health")
def health():
    return {"status": "ok", "service": "shakti360-api"}

@app.get("/ready")
def ready():
    try:
        with engine.connect() as connection:
            connection.exec_driver_sql("SELECT 1")
        return {"status": "ready", "database": "available"}
    except Exception:
        raise HTTPException(503, "Service is not ready")

@app.post("/journeys", response_model=JourneyState)
def create_journey(req: JourneyCreate):
    now = datetime.now(timezone.utc)
    jid = str(uuid4())
    battery = battery_guardian(req.battery_percent)
    state = JourneyState(
        id=jid,
        origin=req.origin,
        destination=req.destination,
        started_at=now,
        expected_arrival=now + timedelta(minutes=req.eta_minutes),
        battery_percent=req.battery_percent,
        power_mode=battery["mode"],
        escalation_level="normal",
        missed_checkins=0,
        active=True,
    )
    journeys[jid] = state.model_dump()
    try:
        track("journey.started", {"journey_id": jid})
    except NameError:
        pass
    return state

@app.get("/journeys/{journey_id}")
def get_journey(journey_id: str):
    if journey_id not in journeys:
        raise HTTPException(404, "Journey not found")
    return journeys[journey_id]

@app.post("/journeys/checkin")
def checkin(req: CheckinRequest):
    if req.journey_id not in journeys:
        raise HTTPException(404, "Journey not found")

    j = journeys[req.journey_id]

    if req.battery_percent is not None:
        j["battery_percent"] = req.battery_percent
        j["power_mode"] = battery_guardian(req.battery_percent)["mode"]

    if req.arrived or req.user_safe is True:
        j["active"] = False
        j["escalation_level"] = "normal"
        try:
            track("journey.completed", {"journey_id": j["id"]})
        except NameError:
            pass
        return {"journey": j, "action": "journey_complete", "temporary_location_session_should_end": True}

    j["missed_checkins"] += 1
    j["escalation_level"] = escalation_engine(j["missed_checkins"])
    try:
        track("journey.missed_checkin", {"journey_id": j["id"]})
    except NameError:
        pass
    return {
        "journey": j,
        "action": j["escalation_level"],
        "message": "Deterministic escalation policy applied."
    }

@app.post("/journeys/{journey_id}/sos")
def explicit_sos(journey_id: str):
    if journey_id not in journeys:
        raise HTTPException(404, "Journey not found")
    journeys[journey_id]["escalation_level"] = escalation_engine(0, explicit_sos=True)
    return {
        "journey": journeys[journey_id],
        "action": "show_emergency_options",
        "note": "Production app should surface verified local emergency options and user-configured trusted contacts."
    }

@app.post("/resources/nearby")
def nearby_resources(req: NearbyRequest):
    return {
        "resources": nearby(req.latitude, req.longitude, req.radius_km),
        "data_note": "Demo resource dataset only. Replace with verified provider data for production."
    }

@app.post("/agents/cyber")
def cyber(req: CyberRequest):
    try:
        track("cyber.scan")
    except NameError:
        pass
    return cyber_guardian(req.text)

@app.post("/agents/privacy")
def privacy(req: PrivacyRequest):
    try:
        track("privacy.check")
    except NameError:
        pass
    return privacy_guardian(req.model_dump())

@app.post("/incidents")
def create_incident(req: IncidentCreate):
    record = {
        "id": str(uuid4()),
        **req.model_dump(),
        "created_at": datetime.now(timezone.utc)
    }
    record["ai_summary"] = evidence_summarizer(
        req.title, req.description, req.occurred_at, req.location, req.tags
    )
    incidents.append(record)
    try:
        track("incident.created", {"incident_id": record["id"]})
    except NameError:
        pass
    return record

@app.get("/incidents")
def list_incidents():
    return {"incidents": incidents}

# ---- Pro / deeper agentic endpoints ----
from .models import SafeWordRequest, ContextRequest, ReadinessRequest, FeedbackRequest
from .policy import EscalationPolicy
from .deep_agents import BatteryGuardian, ContextFusionAgent, CyberGuardian as DeepCyberGuardian, PrivacyGuardian as DeepPrivacyGuardian, ReadinessAgent, PatternAgent
from .analytics import track, add_feedback, impact
from .trusted_circle import notify_demo
from .resource_provider import nearby_live
from .safety_engine import BatteryPolicyEngine

battery_agent = BatteryGuardian()
context_agent = ContextFusionAgent()
deep_cyber_agent = DeepCyberGuardian()
deep_privacy_agent = DeepPrivacyGuardian()
readiness_agent = ReadinessAgent()
pattern_agent = PatternAgent()

@app.get("/agents")
def list_agents():
    return {"agents": [
        "journey_guardian", "battery_guardian", "context_fusion", "safeword_guardian",
        "trusted_circle", "nearby_help", "cyber_guardian", "evidence_guardian",
        "pattern_agent", "privacy_guardian", "safety_readiness", "impact_analytics"
    ]}

@app.post("/agents/context")
def context(req: ContextRequest):
    return context_agent.run(req.model_dump())

@app.post("/readiness")
def readiness(req: ReadinessRequest):
    track("readiness.check")
    return readiness_agent.run(req.model_dump())

@app.post("/journeys/safeword")
def safeword(req: SafeWordRequest):
    if req.journey_id not in journeys:
        raise HTTPException(404, "Journey not found")
    matched = req.phrase.strip().lower() == "blue notebook"
    if not matched:
        return {"matched": False, "action": "none"}
    decision = EscalationPolicy.decide(journeys[req.journey_id]["missed_checkins"], safeword=True)
    journeys[req.journey_id]["escalation_level"] = decision.escalation_level
    deliveries = notify_demo("safeword_triggered", req.journey_id)
    track("journey.safeword", {"journey_id": req.journey_id})
    return {"matched": True, "decision": decision.__dict__, "deliveries": deliveries}

@app.get("/incidents/patterns")
def patterns():
    normalized = []
    for i in incidents:
        normalized.append({
            "description": i.get("description", ""),
            "tags": i.get("tags", []),
        })
    return pattern_agent.run(normalized)

@app.post("/feedback")
def save_feedback(req: FeedbackRequest):
    add_feedback(req.rating, req.useful, req.text)
    return {"status": "saved"}

@app.get("/analytics/impact")
def analytics_impact():
    result = impact()
    result["guardians_connected"] = len(guardians)
    result["active_sos_sessions"] = sum(1 for session in sos_sessions.values() if session["status"] == "active")
    result["data_label"] = "LIVE SESSION DATA"
    return result

@app.post("/resources/nearby-v2")
async def nearby_resources_v2(req: NearbyRequest):
    result = await nearby_live(req.latitude, req.longitude, req.radius_km)
    result["safety_note"] = "Community location data can be incomplete. Verify details before relying on a listing."
    return result

@app.post("/battery/policy")
def battery_policy(payload: BatteryPolicyRequest):
    return BatteryPolicyEngine.decide(**payload.model_dump())

# ---- Guardian Circle and explicit SOS sessions ----
from .models import GuardianAlert, GuardianCreate, GuardianInviteSend, SOSCreate, SOSCancel
from .notifications import invite_url, provider_status, send_guardian_alert, send_guardian_invite

@app.get("/notifications/status")
def notification_status(user: User = Depends(current_user)):
    return {"providers": provider_status(), "operational": all(item["configured"] for item in provider_status().values())}

@app.get("/guardians")
def list_guardians(user: User = Depends(current_user)):
    owned = [guardian for guardian in guardians.values() if guardian["owner_user_id"] == user.id]
    return {"guardians": sorted(owned, key=lambda x: x["priority"]), "storage": "hackathon_session"}

@app.post("/guardians")
def add_guardian(req: GuardianCreate, user: User = Depends(current_user), csrf_cookie: str | None = Cookie(None, alias="shakti_csrf"), csrf_header: str | None = Header(None, alias="X-CSRF-Token")):
    require_csrf(csrf_cookie, csrf_header)
    guardian_id = str(uuid4())
    token = secrets.token_urlsafe(24)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
    record = {"id": guardian_id, "owner_user_id": user.id, **req.model_dump(mode="json"), "invite_token": token, "invite_expires_at": expires_at, "status": "invited", "created_at": datetime.now(timezone.utc)}
    guardians[guardian_id] = record
    track("guardian.invited", {"guardian_id": guardian_id})
    return record

@app.post("/guardians/{guardian_id}/send-invite")
async def deliver_guardian_invite(guardian_id: str, req: GuardianInviteSend, user: User = Depends(current_user), csrf_cookie: str | None = Cookie(None, alias="shakti_csrf"), csrf_header: str | None = Header(None, alias="X-CSRF-Token")):
    require_csrf(csrf_cookie, csrf_header)
    guardian = guardians.get(guardian_id)
    if not guardian or guardian["owner_user_id"] != user.id:
        raise HTTPException(404, "Guardian not found")
    if guardian["invite_expires_at"] < datetime.now(timezone.utc):
        raise HTTPException(410, "Invitation expired")
    results = await send_guardian_invite(guardian, list(dict.fromkeys(req.channels)))
    guardian["delivery"] = results
    if any(result["status"] == "queued" for result in results):
        guardian["status"] = "invite sent"
    track("guardian.invite_delivery", {"guardian_id": guardian_id, "channels": req.channels, "statuses": [r["status"] for r in results]})
    return {"guardian_id": guardian_id, "invite_url": invite_url(guardian["invite_token"]), "deliveries": results}

@app.delete("/guardians/{guardian_id}")
def delete_guardian(guardian_id: str, user: User = Depends(current_user), csrf_cookie: str | None = Cookie(None, alias="shakti_csrf"), csrf_header: str | None = Header(None, alias="X-CSRF-Token")):
    require_csrf(csrf_cookie, csrf_header)
    if guardian_id not in guardians or guardians[guardian_id]["owner_user_id"] != user.id:
        raise HTTPException(404, "Guardian not found")
    del guardians[guardian_id]
    return {"status": "removed"}

@app.get("/guardian-invites/{token}")
def guardian_invite(token: str):
    match = next((g for g in guardians.values() if secrets.compare_digest(g["invite_token"], token)), None)
    if not match:
        raise HTTPException(404, "Invitation not found")
    if match["invite_expires_at"] < datetime.now(timezone.utc):
        raise HTTPException(410, "Invitation expired")
    return {"guardian": {"name": match["name"], "relationship": match["relationship"]}, "permissions": {"journey_started": match["journey_started"], "missed_checkin": match["missed_checkin"], "sos": match["sos"], "live_location": match["live_location"]}, "expires_at": match["invite_expires_at"]}

@app.post("/guardians/notify")
async def notify_guardians(req: GuardianAlert, user: User = Depends(current_user), csrf_cookie: str | None = Cookie(None, alias="shakti_csrf"), csrf_header: str | None = Header(None, alias="X-CSRF-Token")):
    require_csrf(csrf_cookie, csrf_header)
    permission = {"journey_started": "journey_started", "missed_checkin": "missed_checkin", "sos": "sos", "journey_completed": "journey_started", "sos_cancelled": "sos"}[req.event]
    recipients = [g for g in guardians.values() if g["owner_user_id"] == user.id and g.get(permission)]
    event_id = str(uuid4())
    deliveries = []
    for guardian in recipients:
        results = await send_guardian_alert(guardian, req.event, req.message, req.location_url, event_id)
        deliveries.append({"guardian_id": guardian["id"], "guardian_name": guardian["name"], "results": results})
    track("guardian.alert_delivery", {"event_id": event_id, "event": req.event, "guardian_count": len(recipients)})
    return {"event_id": event_id, "event": req.event, "recipient_count": len(recipients), "deliveries": deliveries}

@app.post("/sos")
async def create_sos(req: SOSCreate, user: User = Depends(current_user), csrf_cookie: str | None = Cookie(None, alias="shakti_csrf"), csrf_header: str | None = Header(None, alias="X-CSRF-Token")):
    require_csrf(csrf_cookie, csrf_header)
    sos_id = str(uuid4())
    now = datetime.now(timezone.utc)
    owned = [g for g in guardians.values() if g["owner_user_id"] == user.id and g["sos"]]
    deliveries = []
    for guardian in owned:
        results = await send_guardian_alert(guardian, "sos", None, None, sos_id)
        deliveries.append({"guardian_id": guardian["id"], "guardian_name": guardian["name"], "results": results})
    notified = [g["name"] for g in owned]
    session = {"id": sos_id, "owner_user_id": user.id, "status": "active", "started_at": now, "journey_id": req.journey_id, "battery_percent": req.battery_percent, "guardians_notified": notified, "deliveries": deliveries, "location_session_expires_at": now + timedelta(hours=2), "emergency_services_contacted": False}
    sos_sessions[sos_id] = session
    track("sos.started", {"sos_id": sos_id, "guardian_count": len(notified)})
    return session

@app.post("/sos/{sos_id}/cancel")
async def cancel_sos(sos_id: str, req: SOSCancel, user: User = Depends(current_user), csrf_cookie: str | None = Cookie(None, alias="shakti_csrf"), csrf_header: str | None = Header(None, alias="X-CSRF-Token")):
    require_csrf(csrf_cookie, csrf_header)
    if sos_id not in sos_sessions or sos_sessions[sos_id]["owner_user_id"] != user.id:
        raise HTTPException(404, "SOS session not found")
    sos_sessions[sos_id]["status"] = "cancelled"
    sos_sessions[sos_id]["ended_at"] = datetime.now(timezone.utc)
    sos_sessions[sos_id]["cancel_reason"] = req.reason
    track("sos.cancelled", {"sos_id": sos_id})
    return sos_sessions[sos_id]
