import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from core.config import settings


class MailSender:
    smtp_server_port = settings.SMTP_SERVER_PORT
    smtp_server = settings.SMTP_SERVER
    sender_email = settings.SENDER_EMAIL
    sender_password = settings.SENDER_PASSWORD

    @staticmethod
    def create_msg(user_name, new_pass):
        html = f"""
        <html>
        <body>
            <h3>Password recovery</h3>
            Dear <strong>{user_name}</strong> you requested password recovery on Job platform. You new password:
            <center><h3>{new_pass}</h3></center>
        </body>
        </html>
        """
        return html

    @staticmethod
    def send_msg(user_name, receiver_email, new_pass):
        html = MailSender.create_msg(user_name, new_pass)
        message = MIMEMultipart("alternative")
        message["Subject"] = "Password recovery"
        message["From"] = MailSender.sender_email

        part = MIMEText(html, "html")

        message.attach(part)
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(
            MailSender.smtp_server, MailSender.smtp_server_port, context=context
        ) as server:
            server.login(MailSender.sender_email, MailSender.sender_password)
            message["To"] = receiver_email
            server.sendmail(
                MailSender.sender_email, receiver_email, message.as_string()
            )

        return "MSG was send"
