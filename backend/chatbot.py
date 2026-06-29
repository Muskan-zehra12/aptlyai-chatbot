import os
import re
from datetime import datetime

SYSTEM_PROMPT = """You are AptlyAI, a polite AI appointment booking assistant.
Ask one question at a time and collect: name, email, phone, required service, preferred date and time.
Keep replies short, professional, and helpful. If the user asks unrelated questions, gently bring them back to booking.
"""

FIELD_PATTERN = re.compile(
    r"\b(name|email|phone|service|date|time)\s*:\s*(.*?)(?=\s+\b(?:name|email|phone|service|date|time)\s*:|$)",
    re.IGNORECASE,
)
EMAIL_PATTERN = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_PATTERN = re.compile(r"(?:\+?\d[\d\s().-]{7,}\d)")
TIME_PATTERN = re.compile(r"\b\d{1,2}(?::\d{2})?\s*(?:am|pm|AM|PM)?\b")


def _normalize_date(value: str) -> str:
    value = value.strip().rstrip(".,")
    formats = [
        "%Y-%m-%d",
        "%d %B %Y",
        "%d %b %Y",
        "%B %d %Y",
        "%b %d %Y",
        "%d/%m/%Y",
        "%m/%d/%Y",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(value, fmt).date().isoformat()
        except ValueError:
            pass
    return value


def _normalize_time(value: str) -> str:
    value = value.strip().rstrip(".,").upper().replace(" ", "")
    formats = ["%I:%M%p", "%I%p", "%H:%M", "%H"]
    for fmt in formats:
        try:
            return datetime.strptime(value, fmt).time().strftime("%H:%M")
        except ValueError:
            pass
    return value


def extract_appointment_details(message: str) -> dict:
    details = {}
    for match in FIELD_PATTERN.finditer(message):
        key = match.group(1).lower()
        value = match.group(2).strip(" .,\n\t")
        if value:
            details[key] = value

    if "email" not in details:
        email_match = EMAIL_PATTERN.search(message)
        if email_match:
            details["email"] = email_match.group(0)

    if "phone" not in details:
        phone_match = PHONE_PATTERN.search(message)
        if phone_match:
            details["phone"] = phone_match.group(0).strip()

    if "date" in details:
        details["date"] = _normalize_date(details["date"])

    if "time" in details:
        details["time"] = _normalize_time(details["time"])

    return details


def missing_appointment_fields(details: dict) -> list[str]:
    required = ["name", "email", "phone", "service", "date", "time"]
    return [field for field in required if not details.get(field)]

def fallback_reply(message: str) -> str:
    details = extract_appointment_details(message)
    missing = missing_appointment_fields(details)
    if details and missing:
        return f"Thanks. Please share your {', '.join(missing)} so I can create the appointment request."
    m = message.lower()
    if any(x in m for x in ["hi", "hello", "hey", "salam", "assalam"]):
        return "Hello! I can help you book an appointment. May I have your full name?"
    if "email" in m or "@" in m:
        return "Great. Please share your phone number and the service you want to book."
    if any(x in m for x in ["book", "appointment", "meeting", "demo"]):
        return "Sure. Please share your name, email, phone, service, and preferred date/time."
    if any(x in m for x in ["price", "cost", "fee"]):
        return "Pricing depends on the service. I can capture your details so our team can follow up. What service are you interested in?"
    return "Thanks. To book your appointment, please share your name, email, phone, service, and preferred date/time."

async def get_ai_reply(message: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return fallback_reply(message)
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        result = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": message}],
            temperature=0.3,
        )
        return result.choices[0].message.content
    except Exception:
        return fallback_reply(message)
