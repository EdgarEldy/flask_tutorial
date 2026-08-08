from flask_mail import Message

from flask_tutorial.extensions import mail


class EmailService:
    def send(self, to: str, subject: str, html_body: str) -> None:
        mail.send(Message(subject=subject, recipients=[to], html=html_body))
