from app.core.email.renderer import EmailRenderer
from app.core.email.sender import SMTPEmailSender
from app.core.email.service import EmailService


def get_email_renderer() -> EmailRenderer:
    return EmailRenderer()


def get_email_sender() -> SMTPEmailSender:
    return SMTPEmailSender()


def get_email_service() -> EmailService:
    sender = SMTPEmailSender()
    renderer = EmailRenderer()

    return EmailService(
        sender=sender,
        renderer=renderer,
    )