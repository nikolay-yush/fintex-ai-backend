from abc import ABC, abstractmethod

import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.settings import settings


class BaseEmailSender(ABC):

    @abstractmethod
    async def send(
        self,
        recipient: str,
        subject: str,
        html: str,
    ) -> None:
        ...


class SMTPEmailSender(BaseEmailSender):

    async def send(
        self,
        recipient: str,
        subject: str,
        html: str,
    ) -> None:

        message = MIMEMultipart("alternative")

        message["Subject"] = subject
        message["From"] = (
            f"{settings.mail.FROM_NAME} "
            f"<{settings.mail.FROM}>"
        )
        message["To"] = recipient

        message.attach(
            MIMEText(
                html,
                "html",
            )
        )

        await aiosmtplib.send(
            message,
            hostname=settings.mail.SERVER,
            port=settings.mail.PORT,
            username=settings.mail.USERNAME,
            password=settings.mail.PASSWORD,
            start_tls=settings.mail.STARTTLS,
            use_tls=settings.mail.SSL_TLS,
        )