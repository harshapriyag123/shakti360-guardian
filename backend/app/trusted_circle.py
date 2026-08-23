from datetime import datetime, timezone

DELIVERIES = []

def notify_demo(event_type: str, journey_id: str, contacts: list[dict] | None = None):
    contacts = contacts or [{"name": "Trusted Contact", "channel": "demo", "destination": "demo"}]
    results = []
    for contact in contacts:
        result = {
            "event_type": event_type,
            "journey_id": journey_id,
            "contact": contact,
            "status": "demo_logged",
            "at": datetime.now(timezone.utc).isoformat(),
        }
        DELIVERIES.append(result)
        results.append(result)
    return results
