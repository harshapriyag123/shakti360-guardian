from app.policy import EscalationPolicy

def test_escalation_sequence():
    assert EscalationPolicy.decide(0).escalation_level == "normal"
    assert EscalationPolicy.decide(1).escalation_level == "check"
    assert EscalationPolicy.decide(2).escalation_level == "verify"
    assert EscalationPolicy.decide(3).escalation_level == "trusted_circle"

def test_safeword():
    d = EscalationPolicy.decide(0, safeword=True)
    assert d.notify_trusted_circle is True

def test_explicit_sos():
    d = EscalationPolicy.decide(0, explicit_sos=True)
    assert d.show_emergency_options is True
