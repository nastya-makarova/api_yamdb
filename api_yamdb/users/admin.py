from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


@admin.register(CustomUser)
class UserAdmin(UserAdmin):
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "role",
    )

    list_editable = (
        "first_name",
        "last_name",
        "email",
        "role",
    )


UserAdmin.fieldsets += (
    ("Биография", {"fields": ("bio",)}),
    ("Роль", {"fields": ("role",)}),
)
