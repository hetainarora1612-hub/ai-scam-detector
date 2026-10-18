import joblib
from explain import explain, find_links

model = joblib.load("model.pkl")
vec = joblib.load("vec.pkl")


def clean(text):
    """Turn disguised links like hxxp://bit[dot]ly back into normal ones."""
    t = text.replace("[dot]", ".").replace("(dot)", ".")
    return t.replace("hxxp", "http").replace("HXXP", "http")


def analyze(text):
    """Takes a message, returns the full verdict as a dictionary."""
    text = clean(text)
    ai = float(model.predict_proba(vec.transform([text]))[0][1])
    reasons, rule_score = explain(text)
    final = ai + (1 - ai) * rule_score * 0.8

    if final >= 0.6:
        verdict = "SCAM"
    elif final >= 0.4:
        verdict = "SUSPICIOUS"
    else:
        verdict = "SAFE"

    links = [{"link": l, "warnings": w} for l, w in find_links(text)]

    return {
        "verdict": verdict,
        "scam_percent": round(final * 100),
        "ai_percent": round(ai * 100),
        "reasons": reasons,
        "links": links,
    }