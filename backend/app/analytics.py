from collections import Counter
from datetime import datetime, timezone

_EVENTS = []
_FEEDBACK = []

def track(name: str, payload: dict | None = None):
    _EVENTS.append({"name": name, "payload": payload or {}, "at": datetime.now(timezone.utc).isoformat()})

def add_feedback(rating: int, useful: bool, text: str = ""):
    _FEEDBACK.append({"rating": rating, "useful": useful, "text": text})

def impact():
    c = Counter(e["name"] for e in _EVENTS)
    avg = round(sum(x["rating"] for x in _FEEDBACK) / len(_FEEDBACK), 2) if _FEEDBACK else None
    return {
        "journeys_started": c["journey.started"],
        "journeys_completed": c["journey.completed"],
        "missed_checkins": c["journey.missed_checkin"],
        "safewords_triggered": c["journey.safeword"],
        "cyber_scans": c["cyber.scan"],
        "incidents_documented": c["incident.created"],
        "privacy_checks": c["privacy.check"],
        "readiness_checks": c["readiness.check"],
        "feedback_count": len(_FEEDBACK),
        "average_rating": avg,
        "useful_feedback_count": sum(1 for x in _FEEDBACK if x["useful"]),
    }
