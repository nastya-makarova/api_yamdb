from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models

from api_yamdb.constants import MAX_LENGTH_CONFIRMATION_CODE_FIELD

ADMIN = "admin"
USER = "user"
MODERATOR = "moderator"
CHOICES = (USER, MODERATOR, ADMIN)


class CustomUser(AbstractUser):
    confirmation_code = models.CharField(
        verbose_name="Код подтверждения",
        max_length=MAX_LENGTH_CONFIRMATION_CODE_FIELD,
        null=True,
        blank=True,
    )
    bio = models.TextField("Биография", blank=True)
    role = models.CharField(
        verbose_name="Роль",
        max_length=max(len(role) for role in CHOICES),
        default=USER,
        choices=zip(CHOICES, CHOICES),
    )

    @property
    def is_admin(self):
        return self.role == ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == MODERATOR

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


User = get_user_model()
