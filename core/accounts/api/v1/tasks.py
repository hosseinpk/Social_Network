from celery import shared_task
from mail_templated import EmailMessage


@shared_task
def send_email(email, token):

    mail = EmailMessage(
        "email/mail.tpl", {"token": token}, "from@example.com", to=[email]
    )
    mail.send()

    return "email sent"


@shared_task
def forget_password(email, token):
    mail = EmailMessage(
        "email/forgotpassword.tpl", {"token": token}, "from@example.com", to=[email]
    )
    mail.send()
    return "email sent"