from app.core.email.sender import BaseEmailSender
from app.core.email.renderer import EmailRenderer
from app.core.settings import settings

class EmailService:

    def __init__(
        self,
        sender: BaseEmailSender,
        renderer: EmailRenderer
    ) -> None:
        self.sender = sender
        self.renderer = renderer

    async def send_verification_email(
        self,
        recipient: str,
        token: str,
    ) -> None:

        verification_url = (
            f"{settings.app.HOST_PROTOCOL}://{settings.app.HOST}:{settings.app.PORT}"
            f"/api/v1/auth/verify-email"
            f"?token={token}"
        )

        html = self.renderer.render(
            "verify_email.html",
            verification_url=verification_url,
        )

        await self.sender.send(
            recipient=recipient,
            subject="Verify your email",
            html=html,
        )

    async def send_reset_password_email(
        self,
        recipient: str,
        token: str,
    ) -> None:

        reset_password_url = (
            f"{settings.app.HOST_PROTOCOL}://{settings.app.HOST}:{settings.app.PORT}"
            f"/api/v1/auth/reset-password"
            f"?token={token}"
        )

        html = self.renderer.render(
            "reset_password.html",
            reset_password_url=reset_password_url,
        )

        await self.sender.send(
            recipient=recipient,
            subject="Reset your password",
            html=html,
        )