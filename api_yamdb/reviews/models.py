from datetime import datetime

from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from api_yamdb.constants import MAX_LENGTH_NAME, MAX_LENGTH_SLUG

User = get_user_model()


class Genre(models.Model):
    """Модель для жанра произведения."""

    name = models.CharField(
        "Имя",
        max_length=MAX_LENGTH_NAME,
        help_text="Имя жанра, не более 256 символов",
    )
    slug = models.SlugField(
        "Слаг",
        unique=True,
        max_length=MAX_LENGTH_SLUG,
        help_text="Уникальный слаг жанра, не более 50 символов",
    )

    class Meta:
        ordering = ("id",)
        verbose_name = "жанр"
        verbose_name_plural = "Жанры"

    def __str__(self):
        return self.slug


class Category(models.Model):
    """Модель для категории произведения."""

    name = models.CharField(
        "Имя",
        max_length=MAX_LENGTH_NAME,
        help_text="Имя категории, не более 256 символов",
    )
    slug = models.SlugField(
        "Слаг",
        unique=True,
        max_length=MAX_LENGTH_SLUG,
        help_text="Уникальный слаг категории, не более 50 символов",
    )

    class Meta:
        ordering = ("id",)
        verbose_name = "категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.slug


class Title(models.Model):
    """Модель для произведения."""

    name = models.CharField(
        "Имя",
        max_length=MAX_LENGTH_NAME,
        help_text="Название произведения, не более 256 символов",
    )
    year = models.PositiveIntegerField(
        validators=[
            MaxValueValidator(
                datetime.now().year,
                message="Год должен быть не больше текущего."
            ),
        ],
        verbose_name="Год", help_text="Год выпуска, не больше текущего года"
    )
    description = models.TextField(
        "Описание", blank=True, help_text="Описание произведения"
    )

    genre = models.ManyToManyField(
        Genre,
        blank=True,
        related_name="titles",
        through="GenreTitle",
        verbose_name="Жанр",
        help_text="Жанр произведения",
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="titles",
        verbose_name="Категория",
        help_text="Категория произведения",
    )

    class Meta:
        ordering = ("id",)
        verbose_name = "произведение"
        verbose_name_plural = "Произведения"

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    """Модель для связи между жанрами и произведениями.
    Связь между произведением и жанрами многие-к-многим.
    """

    genre = models.ForeignKey(
        Genre, on_delete=models.CASCADE, verbose_name="жанр"
    )
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, verbose_name="произведение"
    )

    class Meta:
        verbose_name = "Жанры Произведения"
        verbose_name_plural = "Жанры Произведения"

    def __str__(self):
        return f"{self.title} {self.genre}"


class Review(models.Model):
    """Модель для отзыва."""

    text = models.TextField(
        verbose_name="текст отзыва",
        help_text="Текст отзыва",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="автор отзыва",
        help_text="Автор отзыва",
    )
    score = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                1, message="Значение оценки должно быть не менее 1"
            ),
            MaxValueValidator(
                10, message="Значение оценки должно быть не более 10"
            ),
        ],
        verbose_name="оценка отзыва",
        help_text="Оценка отзыва",
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата публикации",
        db_index=True,
        help_text="Дата публикации отзыва",
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name="reviews",
        null=True,
        verbose_name="произведение",
        help_text="Название произведения",
    )

    class Meta:
        verbose_name = "Отзыв"
        ordering = ("-pub_date",)

        constraints = (
            models.UniqueConstraint(
                fields=["author", "title"], name="unique_author_title"
            ),
        )

    def __str__(self):
        return self.text


class Comment(models.Model):
    """Модель для комментария."""

    text = models.TextField(
        verbose_name="текст комментария",
        help_text="Текст комментария",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="автор комментария",
        help_text="Автор комментария",
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата публикации",
        db_index=True,
        help_text="Дата публикации комментария",
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="отзыв",
        help_text="Отзыв для комментариев",
    )

    class Meta:
        verbose_name = "Комментарий"
        ordering = ("-pub_date",)

    def __str__(self):
        return self.text
