import smtplib
from email.message import EmailMessage
from core.config import settings

def send_reset_email(to_email: str, subject: str, body: str):
    msg = EmailMessage()
    msg["From"] = settings.EMAIL_SENDER
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.EMAIL_SENDER, settings.EMAIL_PASSWORD)
        server.send_message(msg)
