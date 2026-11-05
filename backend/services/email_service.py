import os
import smtplib

from email.message import EmailMessage

from dotenv import load_dotenv


load_dotenv()


SMTP_HOST = os.getenv(
    "SMTP_HOST",
    "smtp.gmail.com"
)

SMTP_PORT = int(
    os.getenv(
        "SMTP_PORT",
        "587"
    )
)

SMTP_USERNAME = os.getenv(
    "SMTP_USERNAME"
)

SMTP_PASSWORD = os.getenv(
    "SMTP_PASSWORD"
)

SMTP_FROM_EMAIL = os.getenv(
    "SMTP_FROM_EMAIL"
)


def send_password_reset_otp(
    receiver_email: str,
    otp: str
):

    if not all([
        SMTP_USERNAME,
        SMTP_PASSWORD,
        SMTP_FROM_EMAIL,
    ]):
        raise RuntimeError(
            "SMTP configuration is missing."
        )

    message = EmailMessage()

    message["From"] = SMTP_FROM_EMAIL
    message["To"] = receiver_email
    message["Subject"] = (
        "MealMind password reset code"
    )

    message.set_content(
        f"""
Your MealMind password reset code is:

{otp}

This code expires in 10 minutes.

If you did not request a password reset,
you can ignore this email.

MealMind
"""
    )

    with smtplib.SMTP(
        SMTP_HOST,
        SMTP_PORT
    ) as smtp:

        smtp.starttls()

        smtp.login(
            SMTP_USERNAME,
            SMTP_PASSWORD
        )

        smtp.send_message(
            message
        )