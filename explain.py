import re
import html

# Each signal: (reason shown to user, pattern to look for, points added)
SIGNALS = [
    ("Uses urgency or fear",
     r"\b(urgent|urgently|immediately|now|tonight|blocked|locked|suspend\w*|expire\w*|within \d+ hours?|last warning|final notice|turant|abhi|band ho jayega|freeze|frozen|late fee)\b",
     0.25),
    ("Asks for private information (OTP, PIN, CVV, password)",
     r"\b(otp|pin|cvv|password|card number|debit card|aadhaar|6 digit code|2fa|bank details|account number|ifsc)\b",
     0.50),
    ("Contains a suspicious link",
     r"(https?://\S+|www\.\S+|bit\.ly\S*|tinyurl\S*|cutt\.ly\S*|bit\.do\S*|goo\.gl\S*|\S+\.(?:xyz|top|click|link|info|icu|buzz)\b)",
     0.35),
    ("Promises an unrealistic reward",
     r"\b(won|winner|lottery|prize|lucky|inaam|jeeta|lagi hai|cashback|guaranteed|100 percent)\b",
     0.30),
    ("Asks for a fee or payment",
     r"\b(fee|fees|deposit|processing|registration|charges?|pay rs|send rs|gst|fine of|a fine|pay fine|toll|challan)\b",
     0.35),
    ("Pretends to be police, a government office or a bank officer",
     r"\b(cbi|police|rbi|income tax|customs|arrest|warrant|digital arrest|custody|officer)\b",
     0.30),
    ("Asks you to keep it secret, install an app or use remote access",
     r"(do not tell anyone|don't tell anyone|do not inform|\bapk\b|download this app|stay on video call|anydesk|teamviewer|reply yes to begin)",
     0.35),
    ("Asks for gift cards, codes, or to move the chat to Telegram",
     r"(gift cards?|telegram|whatsapp group|send me the (?:code|otp)|2fa code)",
     0.35),
    ("Asks you to call a number or a so-called officer",
     r"(customer care|call (?:this )?number|call the officer|call officer|contact officer|card services)",
     0.25),
]

# Genuine messages say things like "Do not share your OTP". Don't flag those.
SAFE_PHRASES = r"(do not share|don't share|never share|never ask|do not forward|banks never ask|will never ask)"


def explain(message):
    """Returns (list of reasons, rule score from 0 to 1)."""
    text = message.lower()
    reasons = []
    score = 0.0
    is_warning = re.search(SAFE_PHRASES, text)

    for reason, pattern, points in SIGNALS:
        if "private information" in reason and is_warning:
            continue
        if re.search(pattern, text):
            reasons.append(reason)
            score += points

    return reasons, min(score, 1.0)


def highlight(message):
    """Returns the message as HTML with risky words marked in red."""
    low = message.lower()
    is_warning = re.search(SAFE_PHRASES, low)
    spans = []
    for reason, pattern, points in SIGNALS:
        if "private information" in reason and is_warning:
            continue
        for m in re.finditer(pattern, message, flags=re.IGNORECASE):
            spans.append((m.start(), m.end()))

    spans.sort()
    merged = []
    for s, e in spans:
        if merged and s <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(e, merged[-1][1]))
        else:
            merged.append((s, e))

    out, pos = "", 0
    for s, e in merged:
        out += html.escape(message[pos:s])
        out += ("<mark style='background:#ff4b4b;color:white;"
                "padding:0 3px;border-radius:3px'>" + html.escape(message[s:e]) + "</mark>")
        pos = e
    out += html.escape(message[pos:])
    return out.replace("\n", "<br>")


# ---------- Link checker ----------
LINK_PATTERN = (
    r"(?:https?://|www\.)\S+"
    r"|\b(?:bit\.ly|tinyurl\.com|t\.co|cutt\.ly|goo\.gl|bit\.do)/\S+"
    r"|\b[a-z0-9-]+(?:\.[a-z0-9-]+)*\.(?:xyz|top|click|link|info|icu|buzz|tk|ml|ga|cf)\b\S*"
)
SHORTENERS = ["bit.ly", "tinyurl.com", "t.co", "cutt.ly", "goo.gl", "bit.do"]
RISKY_ENDINGS = [".xyz", ".top", ".click", ".link", ".info", ".icu", ".buzz", ".tk", ".ml", ".ga", ".cf"]
BRAND_WORDS = ["sbi", "hdfc", "icici", "axis", "paytm", "amazon", "netflix", "apple",
               "kyc", "pan", "aadhaar", "refund", "fastag", "login", "verify"]


def find_links(message):
    """Returns a list of (link, [warnings])."""
    results = []
    for match in re.findall(LINK_PATTERN, message, flags=re.IGNORECASE):
        link = match.rstrip(".,;:!?)\"'")
        low = link.lower()
        domain = re.sub(r"^https?://", "", low).split("/")[0]
        warnings = []

        if any(s == domain for s in SHORTENERS):
            warnings.append("Shortened link: it hides the real website")
        if any(domain.endswith(e) for e in RISKY_ENDINGS):
            warnings.append("Risky website ending, often used in scams")
        if low.startswith("http://"):
            warnings.append("Not secure (http, not https)")
        if any(b in domain for b in BRAND_WORDS) and "-" in domain:
            warnings.append("Looks like a fake copy of a bank or service website")
        if low.endswith(".apk"):
            warnings.append("Tries to make you install an app file (APK)")

        results.append((link, warnings))
    return results