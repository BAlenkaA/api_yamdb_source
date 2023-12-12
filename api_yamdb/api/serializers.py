from django.db.models import Avg
from rest_framework import serializers

from reviews.models import Category, Genre, Review, Title


class CategorySerializer(serializers.ModelSerializer):
    lookup_field = 'slug'

    class Meta:
        model = Category
        fields = ("name", "slug",)


class GenreSerializer(serializers.ModelSerializer):
    lookup_field = 'slug'

    class Meta:
        model = Genre
        fields = ("name", "slug",)


class TitleSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(read_only=True, many=True)
    category = CategorySerializer(read_only=True, many=True)
    # rating = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = ("id", "name", "year",
                  "description", "genre", "category",)

    def get_rating(self, obj):
        return Review.objects.select_related(
            "title"
        ).filter(title__id=obj.id).aggregate(Avg('score'))


class CommentSerializer(serializers.ModelSerializer):

    pass


class ReviewSerializer(serializers.ModelSerializer):

    pass
