from dataclasses import dataclass, field
from datetime import datetime, timezone

@dataclass
class PolicyDecision:
    escalation_level: str
    reason: str
    notify_trusted_circle: bool = False
    show_emergency_options: bool = False
    policy_version: str = "1.0"
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class EscalationPolicy:
    """Deterministic, auditable escalation policy."""

    @staticmethod
    def decide(missed_checkins: int, safeword: bool = False, explicit_sos: bool = False) -> PolicyDecision:
        if explicit_sos:
            return PolicyDecision(
                "emergency_options",
                "User explicitly requested emergency options.",
                notify_trusted_circle=True,
                show_emergency_options=True,
            )
        if safeword:
            return PolicyDecision(
                "trusted_circle",
                "Configured SafeWord was triggered.",
                notify_trusted_circle=True,
            )
        if missed_checkins <= 0:
            return PolicyDecision("normal", "No escalation condition met.")
        if missed_checkins == 1:
            return PolicyDecision("check", "First missed check-in.")
        if missed_checkins == 2:
            return PolicyDecision("verify", "Second missed check-in.")
        return PolicyDecision(
            "trusted_circle",
            "Third or later missed check-in.",
            notify_trusted_circle=True,
        )
