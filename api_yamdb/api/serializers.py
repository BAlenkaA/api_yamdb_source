from django.db.models import Avg
from rest_framework import serializers

from reviews.models import Category, Genre, Review, Title


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор категории произведения."""

    class Meta:
        model = Category
        fields = ("name", "slug",)
        lookup_field = 'slug'


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор жанра произведения."""

    class Meta:
        model = Genre
        fields = ("name", "slug",)
        lookup_field = 'slug'


class TitleSafeRequestSerializer(serializers.ModelSerializer):
    """
    Сериализатор произведения для безопасных запросов.
    Необходим для вывода информации о жанре и категории в виде словаря.
    """
    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Title
        fields = ("id", "name", "year",
                  "description", "genre", "category",)


class TitleUnsafeRequestSerializer(serializers.ModelSerializer):
    """
    Сериализатор произведения для небезопасных запросов.
    Необходим для получения информации о жанре и категории в виде слага.
    """
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        fields = (
            'name', 'year', 'description', 'genre', 'category')

    def to_representation(self, title):
        """Переопределение стандартного метода.
        Информация о жанре и категории выводится в виде слага.
        """
        serializer = TitleSafeRequestSerializer(title)
        return serializer.data


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор комментария к отзыву на произведение."""

    pass


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор отзыва на произведение."""

    pass
