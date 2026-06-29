import os

SYSTEM_PROMPT = """You are AptlyAI, a polite AI appointment booking assistant.
Ask one question at a time and collect: name, email, phone, required service, preferred date and time.
Keep replies short, professional, and helpful. If the user asks unrelated questions, gently bring them back to booking.
"""

def fallback_reply(message: str) -> str:
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
