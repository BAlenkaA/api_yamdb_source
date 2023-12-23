from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class CustomUser(AbstractUser):
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'

    ROLE_CHOICES = (
        (USER, 'User'),
        (MODERATOR, 'Moderator'),
        (ADMIN, 'Administrator'),
    )

    bio = models.TextField('Биография', blank=True)
    role = models.CharField(
        'Роль',
        choices=ROLE_CHOICES,
        default='user',
        max_length=20
    )
    confirmation_code = models.CharField(
        'Confirmation Code',
        max_length=100,
        blank=True,
        null=True
    )

    username = models.CharField(
        'Имя пользователя',
        max_length=150,
        unique=True
    )
    email = models.EmailField(
        'Email адрес',
        max_length=254,
        unique=True,
        blank=False,
        null=False
    )

    class Meta:
        ordering = ('username',)

    def __str__(self):
        return self.username


class Genre(models.Model):
    """Модель жанра произведения."""
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class Category(models.Model):
    """Модель категории произведения."""
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class Title(models.Model):
    """Модель произведения, к которому пишут отзывы."""
    name = models.CharField(max_length=256)
    year = models.PositiveIntegerField()
    description = models.TextField()
    genre = models.ManyToManyField(
        Genre,
        related_name='titles_for_genre',
        blank=True,
    )
    rating = models.IntegerField(default=None, null=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='titles_for_category',
        blank=True,
        null=True
    )

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class Review(models.Model):
    """Модель отзыва на произведение."""
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name='reviews_for_title',
        verbose_name='Отзыв')
    text = models.TextField(verbose_name='Текст отзыва')
    author = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        verbose_name='Автор отзыва')
    score = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10)
        ], verbose_name='Оценка'
    )
    pub_date = models.DateTimeField(verbose_name='Дата отзыва',
                                    auto_now_add=True)

    class Meta:
        ordering = ('author',)
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique_author_title'

            )
        ]

    def __str__(self):
        return self.text


class Comment(models.Model):
    """Модель комментария к отзыву на произведение."""
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments_for_review',
        verbose_name='Отзыв')
    text = models.TextField(verbose_name='Текст комментария')
    author = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        verbose_name='Автор комментария')
    pub_date = models.DateTimeField(verbose_name='Дата комментария',
                                    auto_now_add=True)

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text
