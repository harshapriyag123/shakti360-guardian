import re
from collections import Counter

class BatteryGuardian:
    def run(self, battery_percent: int, network: str = "online"):
        if battery_percent < 10:
            mode, strategy, interval = "critical", "essential-events-only", None
        elif battery_percent < 20:
            mode, strategy, interval = "low_power", "reduced-frequency", 600
        elif battery_percent < 50:
            mode, strategy, interval = "balanced", "adaptive", 300
        else:
            mode, strategy, interval = "normal", "event-driven", 180
        if network == "offline":
            strategy = "local-offline"
        return {
            "agent": "battery_guardian",
            "mode": mode,
            "location_strategy": strategy,
            "suggested_check_seconds": interval,
            "continuous_gps_required": False,
            "ai_calls": "minimal" if battery_percent < 20 else "on-demand",
        }

class ContextFusionAgent:
    def run(self, payload: dict):
        score, factors = 0, []
        if payload.get("active_journey"):
            factors.append("active_journey")
        overdue = max(int(payload.get("eta_overdue_minutes", 0)), 0)
        missed = max(int(payload.get("missed_checkins", 0)), 0)
        battery = int(payload.get("battery_percent", 100))
        network = payload.get("network", "online")
        safeword = bool(payload.get("safeword_triggered", False))
        if overdue >= 10:
            score += 15; factors.append("eta_overdue")
        if missed == 1:
            score += 20; factors.append("one_missed_checkin")
        elif missed >= 2:
            score += 35; factors.append("multiple_missed_checkins")
        if battery < 15:
            score += 10; factors.append("low_battery")
        if network != "online":
            score += 10; factors.append("connectivity_degraded")
        if safeword:
            score += 50; factors.append("safeword_triggered")
        state = "elevated" if score >= 60 else "attention" if score >= 25 else "normal"
        return {
            "agent": "context_fusion",
            "context_state": state,
            "context_score": min(score, 100),
            "factors": factors,
            "note": "Session-condition score only; not a prediction of danger.",
        }

class CyberGuardian:
    RULES = [
        ("urgency", r"urgent|immediately|act now|last chance", 14),
        ("credential_request", r"password|otp|verification code|ssn|social security", 26),
        ("money_request", r"gift card|wire transfer|bitcoin|crypto|send money|processing fee", 24),
        ("suspicious_link", r"https?://|bit\\.ly|tinyurl|click here", 14),
        ("threatening_language", r"kill|hurt|harm|watching you|know where you live|you will regret", 34),
        ("secrecy", r"do not tell|keep this secret|don't tell anyone", 15),
    ]
    def run(self, text: str):
        t, score, signals = text.lower(), 0, []
        for name, pattern, weight in self.RULES:
            if re.search(pattern, t):
                signals.append({"signal": name, "weight": weight})
                score += weight
        score = min(score, 100)
        return {
            "agent": "cyber_guardian",
            "risk_level": "high" if score >= 70 else "medium" if score >= 35 else "low",
            "risk_score": score,
            "signals": signals,
            "recommended_actions": [
                "Do not click unknown links or send money based only on the message.",
                "Verify the sender through an independently obtained official channel.",
                "Preserve the message if repeated unwanted contact may need documentation.",
            ],
            "disclaimer": "Signal screening only; not a determination of intent or criminality.",
        }

class PrivacyGuardian:
    def run(self, payload: dict):
        issues, score = [], 100
        if payload.get("location_permission") == "always" and not payload.get("active_journey"):
            issues.append("Always-on location while no journey is active")
            score -= 25
        if payload.get("notification_preview_enabled"):
            issues.append("Sensitive lock-screen notification previews are visible")
            score -= 15
        if not payload.get("evidence_encrypted"):
            issues.append("Evidence encryption is disabled")
            score -= 35
        if not payload.get("app_lock_enabled"):
            issues.append("App lock is disabled")
            score -= 15
        return {"agent": "privacy_guardian", "privacy_score": max(score, 0), "issues": issues}

class ReadinessAgent:
    def run(self, payload: dict):
        checks = [
            ("trusted_contacts", payload.get("trusted_contacts_count", 0) >= 2, 20),
            ("location_privacy", not payload.get("location_always_on", False), 15),
            ("emergency_plan", bool(payload.get("emergency_plan_configured")), 20),
            ("app_lock", bool(payload.get("app_lock_enabled")), 15),
            ("notification_privacy", bool(payload.get("notification_privacy_enabled")), 15),
            ("account_security", bool(payload.get("account_security_reviewed")), 15),
        ]
        score = sum(weight for _, ok, weight in checks if ok)
        return {"agent": "safety_readiness", "score": score, "max_score": 100,
                "missing": [name for name, ok, _ in checks if not ok]}

class PatternAgent:
    def run(self, incidents: list[dict]):
        tag_counts = Counter()
        for i in incidents:
            tag_counts.update(i.get("tags", []))
        observations = [f"{count} incidents share the tag '{tag}'." for tag, count in tag_counts.items() if count >= 2]
        return {
            "agent": "pattern_agent",
            "incident_count": len(incidents),
            "observations": observations,
            "disclaimer": "Descriptive pattern summary only; no inference of guilt or intent.",
        }
