from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueValidator

from reviews.models import Category, Comment, CustomUser, Genre, Review, Title


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор категории произведения."""

    class Meta:
        model = Category
        fields = ('name', 'slug',)
        lookup_field = 'slug'


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор жанра произведения."""

    class Meta:
        model = Genre
        fields = ('name', 'slug',)
        lookup_field = 'slug'


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор отзыва на произведение."""
    author = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date',)
        read_only_fields = ('title', 'pub_date',)

    def validate(self, data):
        if Review.objects.filter(
            author=self.context['request'].user,
            title=self.context['view'].kwargs['title_id']
        ).exists():
            raise serializers.ValidationError(
                'Нельзя отправить отзыв на этот фильм второй раз')
        return data


class ReviewPatchSerializer(serializers.ModelSerializer):
    """Сериализатор отзыва на произведение."""
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
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = ('id', 'name', 'year',
                  'description', 'genre', 'category', 'rating')


class TitleUnsafeRequestSerializer(serializers.ModelSerializer):
    """
    Сериализатор произведения для небезопасных запросов.
    Необходим для получения информации о жанре и категории в виде слага.
    """
    genre = SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True
    )
    category = SlugRelatedField(
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
        raise ValidationError('Username cannot be "me".')


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

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')


class CustomTokenDateNotNull(serializers.ModelSerializer):
    """Сериализатор токена."""
    confirmation_code = serializers.CharField(max_length=100, required=True)
    username = serializers.CharField(max_length=150, required=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'confirmation_code')
        read_only_fields = ['username', 'confirmation_code']


class CustomTokenCodeValidate(CustomTokenDateNotNull):
    """Сериализатор токена."""

    def validate_confirmation_code(self, value):
        if not value or self.instance.confirmation_code != value:
            raise serializers.ValidationError(
                'confirmation_code пустой или указан не верно')
        return value


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
