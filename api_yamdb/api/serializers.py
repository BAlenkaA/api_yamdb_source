from django.core.validators import RegexValidator
from django.db.models import Avg
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from reviews.models import Category, CustomUser, Genre, Review, Title
from rest_framework.relations import SlugRelatedField



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
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        read_only_fields = ('title', 'pub_date')

    def validate(self, data):
        if Review.objects.filter(author=data['author'],
                                 title=self.context['view'].
                                 kwargs['title_id']).exists():
            raise serializers.ValidationError(
                'Нельзя отправить отзыв на этот фильм второй раз')
        else:
            return data


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
        return 0

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


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор отзыва на произведение."""

    pass


class CustomUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=150,
        validators=[
            UniqueValidator(queryset=CustomUser.objects.all()),
            RegexValidator(
                regex=r'^[\w.@+-]+\Z',
                message='Используются недопустимые символы в username'
            )
        ]
    )
    email = serializers.EmailField(
        max_length=254,
        validators=[UniqueValidator(queryset=CustomUser.objects.all())]
    )
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    bio = serializers.CharField(max_length=255, required=False, allow_blank=True)
    role = serializers.ChoiceField(choices=CustomUser.ROLE_CHOICES)


class ParentMeta:
    model = CustomUser
    fields = ('username', 'email')


class UserSignUpSerializer(CustomUserSerializer):

    class Meta(ParentMeta):
        pass


class CustomTokenObtainPairSerialiser(serializers.ModelSerializer):
    token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, attrs):
        username = attrs.get('username')
        confirmation_code = attrs.get('confirmation_code')

        if not username or not confirmation_code:
            raise serializers.ValidationError('Необходимо указать username и confirmation_code')

        try:
            user = CustomUser.objects.get(username=username, confirmation_code=confirmation_code)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError('Пользователь с указанными данными не найден')

    class Meta(ParentMeta):
        fields = ('token', 'username', 'confirmation_code')


class UserProfileSerializer(CustomUserSerializer):
    class Meta(ParentMeta):
        fields = ParentMeta.fields + ('first_name', 'last_name', 'bio', 'role')
        read_only_fields = ('role',)


class UserSerializer(serializers.ModelSerializer):
    class Meta(ParentMeta):
        fields = ParentMeta.fields + ('first_name', 'last_name', 'bio', 'role')
