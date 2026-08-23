from dataclasses import asdict, dataclass

@dataclass(frozen=True)
class BatteryPolicy:
    desired_accuracy: str
    distance_interval_m: int
    time_interval_s: int
    tracking_enabled: bool
    estimated_impact: str
    reason: str
    policy_version: str = "1.0"

class BatteryPolicyEngine:
    """Deterministic adaptive sampling. It never requests continuous GPS polling."""
    @staticmethod
    def decide(*, battery_level: int, charging: bool, movement_state: str, journey_state: str, risk_state: str = "normal", time_since_location_s: int = 0, distance_moved_m: int = 0) -> dict:
        if journey_state not in {"active", "check_in_due", "missed_check_in", "verifying", "escalated"}:
            return asdict(BatteryPolicy("none", 0, 0, False, "none", "Journey is not active; location tracking is stopped."))
        if risk_state == "elevated" or journey_state in {"verifying", "escalated"}:
            return asdict(BatteryPolicy("high", 25, 60, True, "moderate", "User-controlled escalation requires fresher temporary location context."))
        if movement_state == "stationary" and time_since_location_s < 600:
            return asdict(BatteryPolicy("balanced", 250, 600, True, "very low", "Device appears stationary, so updates are reduced."))
        if battery_level <= 15 and not charging:
            return asdict(BatteryPolicy("coarse", 500, 900, True, "very low", "Low battery preserves power with coarse, infrequent updates."))
        if battery_level <= 40 and not charging:
            return asdict(BatteryPolicy("balanced", 150, 420, True, "low", "Medium battery increases the update interval."))
        return asdict(BatteryPolicy("balanced", 75, 180, True, "low", "Active journey uses adaptive, non-continuous sampling."))
