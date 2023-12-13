from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

User = get_user_model()


class Genre(models.Model):
    """Модель жанра произведения."""
    name = models.CharField(max_length=256)
    slug = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    """Модель категории произведения."""
    name = models.CharField(max_length=256)
    slug = models.CharField(max_length=50, unique=True)

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
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='titles_for_category',
        blank=True,
        null=True
    )

    def __str__(self):
        return self.name


class Comment(models.Model):
    """Модель комментария к отзыву на произведение."""

    pass


class Review(models.Model):
    """Модель отзыва на произведение."""
    score = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10)
        ]
    )
