from celery import shared_task
from mail_templated import EmailMessage
from .utils import generate_follow_request_token
from django.contrib.auth import get_user_model

User = get_user_model()


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


@shared_task
def send_follow_request_email(from_user_id, to_user_id):
    from_user = User.objects.get(id=from_user_id)
    to_user = User.objects.get(id=to_user_id)

    accept_token = generate_follow_request_token(from_user_id, "accept")
    reject_token = generate_follow_request_token(from_user_id, "reject")

    mail = EmailMessage(
        "email/acceptorreject_follow_request.tpl",
        {
            "to_user": to_user.username,
            "from_user": from_user.username,
            "accept_token": accept_token,
            "reject_token": reject_token,
        },
        "from@example.com",
        to=[to_user.email],
    )
    mail.send()
    return "follow request email sent"
