import re
from datetime import datetime

from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from rest_framework.serializers import IntegerField

from api.exeptions import ValidationDublicateNotError, ValidationNameError
from api_yamdb.constants import (
    MAX_LENGTH_EMAIL_FIELD,
    MAX_LENGTH_USERNAME_FIELD,
    MAX_LENGTH_CONFIRMATION_CODE_FIELD,
)
from reviews.models import Category, Comment, Genre, Review, Title
from users.models import CHOICES, User


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для модели Category."""

    class Meta:
        model = Category
        fields = ("name", "slug")


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Genre."""

    class Meta:
        model = Genre
        fields = ("name", "slug")


class TitleCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания или изменения объекта Title."""

    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field="slug",
        many=True,
        allow_null=False,
        allow_empty=False,
    )
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(), slug_field="slug"
    )
    description = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Title
        fields = (
            "id",
            "name",
            "year",
            "description",
            "genre",
            "category",
        )

    def validate_year(self, value):
        """Метод проверяет, значение года произведения.
        Год должен быть не больше текущего.
        """
        current_year = datetime.now().year
        if value > current_year or value < 0:
            raise serializers.ValidationError(
                f"Год должен быть больше нуля и меньше {current_year}."
            )
        return value

    def to_representation(self, title):
        """Метод изменяет сериализатор для отображение объекта Title.
        Используется при формировании ответа на POSTили PATCH запрос."""
        serializer = TitleSerializer(title)
        return serializer.data


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения объекта Title."""

    genre = GenreSerializer(many=True)
    category = CategorySerializer()
    description = serializers.CharField(required=False, allow_blank=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = (
            "id",
            "name",
            "year",
            "description",
            "rating",
            "genre",
            "category",
        )


class ValidationUsernameMixin:
    """Миксин для проверки имени пользователя
    на соответствие регулярному выражению
    """

    def validate_username(self, value):
        username_pattern = r"^[\w.@+-]+\Z"
        if value == "me":
            raise serializers.ValidationError(
                "Недопустимое имя пользователя",
            )
        if not re.match(username_pattern, value):
            raise serializers.ValidationError(
                "Недопустимые символы в имени пользователя",
            )
        return value


class UserSerializer(serializers.ModelSerializer, ValidationUsernameMixin):
    email = serializers.EmailField(
        required=True,
        max_length=MAX_LENGTH_EMAIL_FIELD,
    )

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "bio",
            "role",
        )

    def validate(self, data):
        user = User.objects.filter(username=data["username"]).first()
        if user:
            user_mail = user.email
            if user_mail == data["email"]:
                raise ValidationDublicateNotError(
                    "Пользователь с такими данными уже существует"
                )
            if data["email"] != user_mail:
                raise serializers.ValidationError(
                    "Пользователь с таким именем уже существует"
                )
        elif User.objects.filter(email=data["email"]).exists():
            raise serializers.ValidationError(
                "Пользователь с таким email уже существует"
            )
        return data


class UserGetUsernameSerializer(serializers.ModelSerializer):
    """Сериализатор для получения информации о пользователе."""

    role = serializers.ChoiceField(choices=CHOICES)

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "bio",
            "role",
        )


class UserGetMeSerializer(UserGetUsernameSerializer):
    """Сериализатор для получения информации текущим пользователем."""

    role = serializers.ChoiceField(choices=CHOICES, read_only=True)


class SignUpSerializer(serializers.ModelSerializer, ValidationUsernameMixin):
    """Сериализатор для регистрации пользователя."""

    username = serializers.CharField(
        required=True, max_length=MAX_LENGTH_USERNAME_FIELD
    )
    email = serializers.EmailField(
        required=True, max_length=MAX_LENGTH_EMAIL_FIELD
    )

    class Meta:
        model = User
        fields = (
            "username",
            "email",
        )

    def validate(self, data):
        user = User.objects.filter(username=data["username"]).first()
        if user:
            if data["email"] != user.email:
                raise serializers.ValidationError(
                    "Пользователь с таким именем уже существует"
                )
        elif User.objects.filter(email=data["email"]).exists():
            raise serializers.ValidationError(
                "Пользователь с таким email уже существует"
            )

        return data


class GetTokenSerializer(serializers.ModelSerializer):
    """Сериализатор для получения токена."""

    username = serializers.CharField(
        required=True, max_length=MAX_LENGTH_USERNAME_FIELD
    )
    confirmation_code = serializers.CharField(
        required=True, max_length=MAX_LENGTH_CONFIRMATION_CODE_FIELD
    )

    class Meta:
        model = User
        fields = ("username", "confirmation_code")

    def validate_username(self, value):
        if not User.objects.filter(username=value).exists():
            raise ValidationNameError(
                detail="Такого пользователя не существует",
            )
        return value

    def validate(self, data):
        user = get_object_or_404(User, username=data["username"])
        confirmation_code = data["confirmation_code"]
        if user.confirmation_code != confirmation_code:
            raise serializers.ValidationError("Неверный код подтверждения")
        return data


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Review."""

    author = serializers.StringRelatedField(read_only=True)
    score = IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )

    class Meta:
        model = Review
        fields = ("id", "text", "author", "score", "pub_date")

    def validate(self, data):
        """Разрешает добавлять пользователю только один отзыв."""
        if self.context.get("request").method != "POST":
            return data
        author = self.context.get("request").user
        title_id = self.context.get("view").kwargs.get("title_id")
        if Review.objects.filter(author=author, title=title_id).exists():
            raise serializers.ValidationError(
                "У Вас уже есть отзыв на это произведение"
            )
        return data


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Comment."""

    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ("id", "text", "author", "pub_date")
