from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db.models import Avg
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueValidator

from reviews.models import Category, Comment, CustomUser, Genre, Review, Title


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


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор отзыва на произведение."""
    author = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date',)
        read_only_fields = ('title', 'pub_date',)

    def validate(self, data):
        if Review.objects.filter(author=self.context.get('request').user,
                                 title=self.context['view'].
                                 kwargs['title_id']).exists():
            raise serializers.ValidationError(
                'Нельзя отправить отзыв на этот фильм второй раз')
        return data


class ReviewPatchSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date',)
        read_only_fields = ('title', 'pub_date',)


class TitleSafeRequestSerializer(serializers.ModelSerializer):
    """
    Сериализатор произведения для безопасных запросов.
    Необходим для вывода информации о жанре и категории в виде словаря.
    """
    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    rating = serializers.SerializerMethodField()

    def get_rating(self, obj):
        if Review.objects.values('score').filter(title=obj.id):
            return int((Review.objects.filter(title=obj.id).
                        aggregate(Avg('score')))['score__avg'])

    class Meta:
        model = Title
        fields = ("id", "name", "year",
                  "description", "genre", "category", "rating")


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
    author = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
        read_only_fields = ('review',)


def validate_username_not_me(value):
    """Валидатор, запрещающий использование me в качестве username."""
    if value.lower() == 'me':
        raise ValidationError("Username cannot be 'me'.")


class CustomUserSerializer(serializers.ModelSerializer):
    """Базовый сериализатор Пользователя."""
    username = serializers.CharField(
        max_length=150,
        validators=[
            UniqueValidator(queryset=CustomUser.objects.all()),
            RegexValidator(
                regex=r'^[\w.@+-]+\Z',
                message='Используются недопустимые символы в username'
            ), validate_username_not_me
        ]
    )
    email = serializers.EmailField(
        max_length=254,
        validators=[UniqueValidator(queryset=CustomUser.objects.all())]
    )
    first_name = serializers.CharField(
        max_length=150,
        required=False,
        allow_blank=True
    )
    last_name = serializers.CharField(
        max_length=150,
        required=False,
        allow_blank=True
    )
    bio = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True
    )
    role = serializers.ChoiceField(
        choices=CustomUser.ROLE_CHOICES,
        required=False
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')


class CustomTokenObtainPairSerializer(serializers.ModelSerializer):
    """Сериализатор токена."""

    def validate(self, data):
        username = data.get('username')
        confirmation_code = data.get('confirmation_code')

        if not username or not confirmation_code:
            raise serializers.ValidationError('Необходимо указать username'
                                              ' и confirmation_code')

        try:
            CustomUser.objects.get(username=username,
                                   confirmation_code=confirmation_code)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError('Пользователь с указанными'
                                              ' данными не найден')

    class Meta:
        model = CustomUser
        fields = ('username', 'confirmation_code')


class UserProfileSerializer(CustomUserSerializer):
    """Сериализатор управления профилем пользователя."""
    role = serializers.ChoiceField(choices=CustomUser.ROLE_CHOICES,
                                   read_only=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')


class UserSerializer(CustomUserSerializer):
    """Сериализатор администратора."""

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')
