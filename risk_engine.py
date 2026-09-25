def calculate_risk_score(
    current_risk,
    location_count,
    recent_count,
    category_count
):
    """Calculate an administrator-facing risk indicator from 0 to 100."""
    score = {
        "Critical": 40,
        "High": 30,
        "Medium": 20,
        "Low": 10,
    }.get(current_risk, 10)

    if location_count >= 10:
        score += 20
    elif location_count >= 5:
        score += 15
    elif location_count >= 2:
        score += 10

    if recent_count >= 10:
        score += 20
    elif recent_count >= 5:
        score += 15
    elif recent_count >= 2:
        score += 10

    if category_count >= 10:
        score += 20
    elif category_count >= 5:
        score += 10
    elif category_count >= 2:
        score += 5

    return min(score, 100)


def get_risk_status(score):
    if score >= 80:
        return "Urgent Review"
    if score >= 60:
        return "Needs Review"
    if score >= 30:
        return "Monitor"
    return "Normal"


def get_recommendation(score):
    if score >= 80:
        return "Immediate administrator review is recommended."
    if score >= 60:
        return "Review the incident and related historical cases."
    if score >= 30:
        return "Continue monitoring incident patterns."
    return "No additional escalation indicated by this score."


def get_escalation_level(score):
    if score >= 80:
        return "Level 3 - Urgent Review"
    if score >= 60:
        return "Level 2 - Admin Review"
    if score >= 30:
        return "Level 1 - Monitor"
    return "Level 0 - Normal"