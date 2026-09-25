"""Small, explicit alert policy for administrator workflows."""


def should_alert(risk_score):
    """Return True when an incident should enter administrator review."""
    return int(risk_score or 0) >= 60


def get_alert_message(risk_score, report_id):
    if should_alert(risk_score):
        return f"Incident {report_id} requires administrator review."
    return None
