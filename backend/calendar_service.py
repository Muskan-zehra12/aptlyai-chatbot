import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


def create_calendar_event(name: str, email: str, service: str, date: str, time: str) -> tuple[str | None, str | None]:
    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    calendar_id = os.getenv("GOOGLE_CALENDAR_ID", "primary")
    timezone = os.getenv("GOOGLE_CALENDAR_TIMEZONE", "UTC")
    duration_minutes = int(os.getenv("APPOINTMENT_DURATION_MINUTES", "30"))

    if not credentials_path:
        return None, "GOOGLE_APPLICATION_CREDENTIALS is not configured"

    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build

        start = datetime.fromisoformat(f"{date}T{time}").replace(tzinfo=ZoneInfo(timezone))
        end = start + timedelta(minutes=duration_minutes)
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=["https://www.googleapis.com/auth/calendar.events"],
        )
        service_client = build("calendar", "v3", credentials=credentials)
        event = {
            "summary": f"AptlyAI appointment: {service}",
            "description": "\n".join(
                [
                    f"Client: {name}",
                    f"Email: {email}",
                    f"Service: {service}",
                ]
            ),
            "start": {"dateTime": start.isoformat(), "timeZone": timezone},
            "end": {"dateTime": end.isoformat(), "timeZone": timezone},
            "attendees": [{"email": email}],
        }
        created_event = service_client.events().insert(calendarId=calendar_id, body=event).execute()
        return created_event.get("id"), None
    except Exception as exc:
        return None, str(exc)
