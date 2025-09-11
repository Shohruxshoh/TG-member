from celery import shared_task
from users.models import User
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from core.settings import EMAIL_HOST_USER

@shared_task
def send_email(email):
    user = User.objects.get(email=email)

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    reset_url = f"http://localhost/api/app/users/reset-password/{uid}/{token}/"

    send_mail(
        subject="Parolni tiklash",
        message=f"Parolni tiklash uchun ushbu havolaga o‘ting: {reset_url}",
        from_email=EMAIL_HOST_USER,
        recipient_list=[email],
    )
    return {"message": "A password reset link has been sent to your email."}