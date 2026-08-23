import re
from typing import Dict, List

def battery_guardian(percent: int) -> Dict:
    if percent < 10:
        return {
            "mode": "critical",
            "location_strategy": "essential-events-only",
            "background_sync": False,
            "ai_calls": "minimal",
            "message": "Critical battery mode: preserve essential safety functions."
        }
    if percent < 20:
        return {
            "mode": "low_power",
            "location_strategy": "reduced-frequency",
            "background_sync": False,
            "ai_calls": "reduced",
            "message": "Low-power mode enabled."
        }
    if percent < 50:
        return {
            "mode": "balanced",
            "location_strategy": "adaptive",
            "background_sync": True,
            "ai_calls": "on-demand",
            "message": "Balanced battery-aware monitoring."
        }
    return {
        "mode": "normal",
        "location_strategy": "event-driven",
        "background_sync": True,
        "ai_calls": "on-demand",
        "message": "Normal battery-aware monitoring."
    }

def escalation_engine(missed_checkins: int, explicit_sos: bool = False) -> str:
    if explicit_sos:
        return "emergency_options"
    if missed_checkins <= 0:
        return "normal"
    if missed_checkins == 1:
        return "check"
    if missed_checkins == 2:
        return "verify"
    return "trusted_circle"

def cyber_guardian(text: str) -> Dict:
    t = text.lower()
    signals: List[Dict] = []

    rules = [
        ("urgency", r"urgent|immediately|act now|today only|last chance", 18),
        ("credential_request", r"password|otp|verification code|ssn|social security|bank login", 28),
        ("money_request", r"gift card|wire transfer|crypto|bitcoin|send money|payment fee", 25),
        ("suspicious_link", r"https?://|bit\.ly|tinyurl|click here", 16),
        ("threatening_language", r"kill|hurt|harm|watching you|know where you live|you will regret", 35),
        ("impersonation", r"hr department|bank security|irs|police department|tech support", 12),
    ]

    score = 0
    for name, pattern, weight in rules:
        if re.search(pattern, t):
            signals.append({"signal": name, "weight": weight})
            score += weight

    score = min(score, 100)
    if score >= 70:
        level = "high"
    elif score >= 35:
        level = "medium"
    else:
        level = "low"

    recommendations = [
        "Do not click unknown links or send money based only on the message.",
        "Verify the sender through an independently obtained official channel.",
        "Preserve the message if you may need to document repeated unwanted contact."
    ]

    return {
        "risk_level": level,
        "risk_score": score,
        "signals": signals,
        "recommendations": recommendations,
        "disclaimer": "This is a signal-based screening result, not a determination of intent or criminality."
    }

def privacy_guardian(data: Dict) -> Dict:
    issues = []
    score = 100

    if data.get("location_permission") == "always" and not data.get("active_journey"):
        issues.append("Location is allowed all the time even though no journey is active.")
        score -= 25

    if data.get("notification_preview_enabled"):
        issues.append("Sensitive notification previews may be visible on the lock screen.")
        score -= 15

    if not data.get("evidence_encrypted"):
        issues.append("Evidence encryption is disabled.")
        score -= 35

    if not data.get("app_lock_enabled"):
        issues.append("App lock is disabled.")
        score -= 15

    return {
        "privacy_score": max(score, 0),
        "issues": issues,
        "status": "good" if score >= 80 else "review"
    }

def evidence_summarizer(title: str, description: str, occurred_at, location, tags):
    facts = []
    if title:
        facts.append(f"Incident title: {title}")
    if occurred_at:
        facts.append(f"Recorded occurrence time: {occurred_at}")
    if location:
        facts.append(f"Recorded location: {location}")
    if description:
        facts.append(f"User description: {description}")
    if tags:
        facts.append("Tags: " + ", ".join(tags))

    return {
        "structured_facts": facts,
        "summary": " | ".join(facts),
        "disclaimer": "Summary reflects only user-provided information and does not infer guilt, intent, or legal status."
    }
