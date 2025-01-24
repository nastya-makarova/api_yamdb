import csv
import os

from django.core.management.base import BaseCommand
from reviews.models import Category, Comment, Genre, GenreTitle, Review, Title
from users.models import CustomUser

TABLES_AND_FILES = {
    CustomUser: "users.csv",
    Category: "category.csv",
    Genre: "genre.csv",
    Title: "titles.csv",
    GenreTitle: "genre_title.csv",
    Review: "review.csv",
    Comment: "comments.csv",
}

FOREIGN_KEYS = {
    "category": ("category", Category),
    "title_id": ("title", Title),
    "genre_id": ("genre", Genre),
    "author": ("author", CustomUser),
    "review_id": ("review", Review),
}


class Command(BaseCommand):
    """Импорт данных из CSV файлов в базу данных.

    Этот класс отвечает за загрузку данных из CSV файлов,
    которые находятся в директории `static/data/`.
    """

    help = "Импорт данных из csv файлов."

    def handle(self, *args, **kwargs):
        """Метод обрабатывает команду импорта csv данных в БД."""
        directory_path = "static/data/"

        for model, filename in TABLES_AND_FILES.items():
            filepath = os.path.join(directory_path, filename)
            print(filepath)

            if not os.path.exists(filepath):
                return f"Файл {filepath} существует."

            with open(filepath, mode="r", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                objects = []
                for data in reader:
                    data_copy = {}
                    for key, value in data.items():
                        if key in FOREIGN_KEYS:
                            new_key = FOREIGN_KEYS[key][0]
                            try:
                                data_copy[new_key] = FOREIGN_KEYS[key][
                                    1
                                ].objects.get(pk=value)
                            except FOREIGN_KEYS[key][1].DoesNotExist:
                                data_copy[new_key] = None
                                return (
                                    f"Связный объект для ключа {key}"
                                    " не существует."
                                )
                        else:
                            data_copy[key] = value

                    object_instance = model(**data_copy)
                    objects.append(object_instance)

                model.objects.bulk_create(objects)
        return "Данные из csv файлов успешно загружены."
