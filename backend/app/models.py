from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import List, Optional, Literal
from datetime import datetime

EscalationLevel = Literal["normal", "check", "verify", "trusted_circle", "emergency_options"]

class JourneyCreate(BaseModel):
    origin: str
    destination: str
    eta_minutes: int = Field(ge=1, le=240)
    battery_percent: int = Field(ge=0, le=100)
    trusted_contacts: List[str] = Field(default_factory=list)

class JourneyState(BaseModel):
    id: str
    origin: str
    destination: str
    started_at: datetime
    expected_arrival: datetime
    battery_percent: int
    power_mode: str
    escalation_level: EscalationLevel
    missed_checkins: int = 0
    active: bool = True

class CheckinRequest(BaseModel):
    journey_id: str
    arrived: bool = False
    user_safe: Optional[bool] = None
    battery_percent: Optional[int] = None

class NearbyRequest(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    radius_km: float = Field(default=5.0, gt=0, le=15)

class CyberRequest(BaseModel):
    text: str

class IncidentCreate(BaseModel):
    title: str
    description: str
    occurred_at: Optional[datetime] = None
    location: Optional[str] = None
    tags: List[str] = Field(default_factory=list, max_length=20)

class PrivacyRequest(BaseModel):
    active_journey: bool
    location_permission: str
    notification_preview_enabled: bool
    evidence_encrypted: bool
    app_lock_enabled: bool

class SafeWordRequest(BaseModel):
    journey_id: str
    phrase: str

class ContextRequest(BaseModel):
    active_journey: bool
    eta_overdue_minutes: int = 0
    missed_checkins: int = 0
    battery_percent: int = Field(ge=0, le=100)
    network: str = "online"
    safeword_triggered: bool = False

class ReadinessRequest(BaseModel):
    trusted_contacts_count: int = Field(ge=0, le=20)
    location_always_on: bool
    emergency_plan_configured: bool
    app_lock_enabled: bool
    notification_privacy_enabled: bool
    account_security_reviewed: bool

class FeedbackRequest(BaseModel):
    rating: int = Field(ge=1, le=5)
    useful: bool = True
    text: str = ""

class GuardianCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    relationship: str = Field(default="trusted contact", max_length=50)
    phone: Optional[str] = Field(default=None, max_length=30)
    email: Optional[EmailStr] = None
    priority: int = Field(default=1, ge=1, le=5)
    journey_started: bool = True
    missed_checkin: bool = True
    sos: bool = True
    live_location: bool = True

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: Optional[str]):
        if value is None or not value.strip():
            return None
        normalized = value.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        if not normalized.startswith("+") or not normalized[1:].isdigit() or not 8 <= len(normalized[1:]) <= 15:
            raise ValueError("Phone must use international E.164 format, for example +15551234567")
        return normalized

class GuardianInviteSend(BaseModel):
    channels: List[Literal["sms", "email"]] = Field(min_length=1, max_length=2)

class GuardianAlert(BaseModel):
    event: Literal["journey_started", "missed_checkin", "sos", "journey_completed", "sos_cancelled"]
    journey_id: Optional[str] = Field(default=None, max_length=100)
    message: Optional[str] = Field(default=None, max_length=240)
    location_url: Optional[str] = Field(default=None, max_length=500)

class SOSCreate(BaseModel):
    journey_id: Optional[str] = None
    battery_percent: Optional[int] = Field(default=None, ge=0, le=100)

class SOSCancel(BaseModel):
    reason: str = Field(default="user_safe", max_length=100)

class BatteryPolicyRequest(BaseModel):
    battery_level: int = Field(ge=0, le=100)
    charging: bool = False
    movement_state: Literal["stationary", "moving", "unknown"] = "unknown"
    journey_state: Literal["created", "active", "check_in_due", "missed_check_in", "verifying", "escalated", "completed", "cancelled"]
    risk_state: Literal["normal", "elevated"] = "normal"
    time_since_location_s: int = Field(default=0, ge=0)
    distance_moved_m: int = Field(default=0, ge=0)
