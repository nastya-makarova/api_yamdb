import random
import string

from django.core.mail import send_mail
from rest_framework_simplejwt.tokens import RefreshToken


characters = string.ascii_letters + string.digits


def generate_password(length=12, characters=characters):
    """Функция генерирует случайный пароль"""
    password = "".join(random.choice(characters) for _ in range(length))
    return password


def send_confirmation_email(message="", recepient_list=[]):
    """Функция отправляет письмо с кодом подтверждения регистрации"""
    send_mail(
        subject="Подтверждение регистрации",
        message=message,
        from_email="from@example.com",
        recipient_list=recepient_list,
        fail_silently=True,
    )


def get_tokens_for_user(user):
    """Функция создает токен для пользователя"""
    refresh = RefreshToken.for_user(user)
    return {
        "token": str(refresh.access_token),
    }
