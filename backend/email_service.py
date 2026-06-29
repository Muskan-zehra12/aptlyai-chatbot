import os
import smtplib
from email.message import EmailMessage


def send_appointment_confirmation(
    to_email: str,
    name: str,
    service: str,
    appointment_date: str,
    appointment_time: str,
) -> tuple[bool, str | None]:
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    email_from = os.getenv("EMAIL_FROM") or smtp_user

    if not smtp_host or not email_from:
        return False, "SMTP is not configured"

    message = EmailMessage()
    message["Subject"] = "Your AptlyAI appointment request is confirmed"
    message["From"] = email_from
    message["To"] = to_email
    message.set_content(
        "\n".join(
            [
                f"Hi {name},",
                "",
                "Thanks for booking with AptlyAI. We received your appointment request.",
                "",
                f"Service: {service}",
                f"Date: {appointment_date}",
                f"Time: {appointment_time}",
                "",
                "Our team will review the request and follow up if anything else is needed.",
                "",
                "AptlyAI Team",
            ]
        )
    )

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
            server.starttls()
            if smtp_user and smtp_password:
                server.login(smtp_user, smtp_password)
            server.send_message(message)
        return True, None
    except Exception as exc:
        return False, str(exc)
