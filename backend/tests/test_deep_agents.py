from app.deep_agents import BatteryGuardian, ContextFusionAgent, CyberGuardian, PrivacyGuardian, ReadinessAgent

def test_battery_guardian_avoids_continuous_gps():
    r = BatteryGuardian().run(8)
    assert r["mode"] == "critical"
    assert r["continuous_gps_required"] is False

def test_context_is_not_danger_prediction():
    r = ContextFusionAgent().run({"active_journey": True, "missed_checkins": 2, "battery_percent": 9, "network": "offline"})
    assert r["context_state"] in {"attention", "elevated"}
    assert "not a prediction" in r["note"]

def test_cyber_signals():
    r = CyberGuardian().run("URGENT: send gift cards now and don't tell anyone")
    assert r["risk_score"] > 0
    assert len(r["signals"]) >= 2

def test_privacy_score():
    r = PrivacyGuardian().run({"active_journey": False, "location_permission": "always", "notification_preview_enabled": True, "evidence_encrypted": False, "app_lock_enabled": False})
    assert r["privacy_score"] < 50

def test_readiness():
    r = ReadinessAgent().run({"trusted_contacts_count": 2, "location_always_on": False, "emergency_plan_configured": True, "app_lock_enabled": True, "notification_privacy_enabled": True, "account_security_reviewed": True})
    assert r["score"] == 100
