from django.contrib import admin

from .models import Category, Comment, Genre, Review, Title, GenreTitle


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "text",
        "author",
        "score",
        "pub_date",
        "title",
    )
    list_filter = ("author", "score", "pub_date")
    search_fields = ("author",)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "text",
        "author",
        "pub_date",
        "review",
    )
    list_filter = ("author", "pub_date")
    search_fields = ("author",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug")
    list_editable = ("name", "slug")
    search_fields = ("name", "slug")
    list_filter = ("name", "slug")


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug")
    list_editable = ("name", "slug")
    search_fields = ("name", "slug")
    list_filter = ("name", "slug")


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "year",
        "description",
        "category",
    )
    list_editable = ("name", "year", "description", "category")
    search_fields = ("name", "year", "category")
    list_filter = ("name", "category", "year")
    empty_value_display = "Не задано"


@admin.register(GenreTitle)
class GenreTitleAdmin(admin.ModelAdmin):
    list_display = ("genre", "title")
    list_filter = ("genre", "title")
