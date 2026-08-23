from app.safety_engine import BatteryPolicyEngine

def test_tracking_stops_after_journey():
    result = BatteryPolicyEngine.decide(battery_level=80, charging=False, movement_state="moving", journey_state="completed")
    assert result["tracking_enabled"] is False
    assert result["desired_accuracy"] == "none"

def test_low_battery_uses_coarse_infrequent_updates():
    result = BatteryPolicyEngine.decide(battery_level=9, charging=False, movement_state="moving", journey_state="active")
    assert result["desired_accuracy"] == "coarse"
    assert result["time_interval_s"] >= 900
    assert result["estimated_impact"] == "very low"

def test_stationary_reduces_updates():
    result = BatteryPolicyEngine.decide(battery_level=90, charging=False, movement_state="stationary", journey_state="active", time_since_location_s=100)
    assert result["distance_interval_m"] >= 250

def test_explicit_escalation_uses_fresher_context():
    result = BatteryPolicyEngine.decide(battery_level=50, charging=False, movement_state="moving", journey_state="escalated", risk_state="elevated")
    assert result["desired_accuracy"] == "high"
    assert result["time_interval_s"] == 60
