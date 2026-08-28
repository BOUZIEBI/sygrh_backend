from email.message import EmailMessage
import aiosmtplib

from app.core.config import settings


async def send_password_reset_email(
    email: str,
    reset_link: str
):
    message = EmailMessage()

    message["From"] = (
        f"{settings.APP_NAME} <{settings.MAIL_FROM}>"
    )
    message["To"] = email
    message["Subject"] = "Réinitialisation de votre mot de passe"

    message.set_content(
        f"""
            Bonjour,

            Vous avez demandé la réinitialisation de votre mot de passe.

            Cliquez sur le lien suivant pour définir un nouveau mot de passe :

            {reset_link}

            Ce lien est valable pendant 30 minutes.

            Si vous n'êtes pas à l'origine de cette demande, vous pouvez ignorer cet email.

            Cordialement,
            {settings.APP_NAME}
        """
    )

    await aiosmtplib.send(
        message,
        hostname=settings.MAIL_HOST,
        port=settings.MAIL_PORT,
        start_tls=True,
        username=settings.MAIL_USERNAME,
        password=settings.MAIL_PASSWORD,
    )