import asyncio

from app.core.email.sender import SMTPEmailSender
from app.core.email.service import EmailService
from app.core.email.renderer import EmailRenderer


async def main() -> None:
    sender = SMTPEmailSender()
    renderer = EmailRenderer()

    email_service = EmailService(
        sender=sender,
        renderer=renderer,
    )

    await email_service.send_verification_email(
        recipient="nik2000shved@gmail.com",
        token="123456789",
    )

    print("Email sent successfully.")


if __name__ == "__main__":
    asyncio.run(main())