def calculate_risk(text):

    text = text.lower()

    critical_words = [
        "weapon",
        "attack",
        "violence",
        "danger",
        "threat",
        "emergency"
    ]

    high_words = [
        "harassment",
        "stalking",
        "hacked",
        "fraud",
        "scam",
        "bullying"
    ]

    medium_words = [
        "suspicious",
        "phishing",
        "broken",
        "fake",
        "problem"
    ]

    if any(word in text for word in critical_words):

        return "Critical"

    if any(word in text for word in high_words):

        return "High"

    if any(word in text for word in medium_words):

        return "Medium"

    return "Low"


# --------------------------------
# AI Incident Analysis
# --------------------------------

def analyze_incident(description):

    text = description.lower()

    keyword_groups = {
        "Cybersecurity": (
            "phishing", "suspicious link", "hacked", "otp", "scam",
            "fraud", "password", "malware", "fake account"
        ),
        "Campus Safety": (
            "threat", "fight", "violence", "harassment", "bullying",
            "danger", "stalking", "attack", "weapon"
        ),
        "Infrastructure": (
            "broken", "electricity", "water", "toilet", "road", "fan",
            "light", "pipe"
        )
    }

    scores = {
        category: sum(keyword in text for keyword in keywords)
        for category, keywords in keyword_groups.items()
    }
    category = max(scores, key=scores.get)
    best_score = scores[category]

    if best_score == 0:
        category = "General"
        confidence = 50.0
    else:
        confidence = min(95.0, 60.0 + best_score * 10.0)

    return category, calculate_risk(description), confidence