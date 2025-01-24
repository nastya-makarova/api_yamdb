import django_filters

from reviews.models import Title


class TitleFilter(django_filters.FilterSet):
    """Фильтр для модели Title.
    Фильтр позволяет фильтровать произведения по различным полям,
    в том числе по слагу жанра и категории.
    """

    genre = django_filters.CharFilter(field_name="genre__slug")
    category = django_filters.CharFilter(field_name="category__slug")

    class Meta:
        model = Title
        fields = ("category", "genre", "year", "name")
