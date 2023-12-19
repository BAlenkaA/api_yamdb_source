from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('user', 'User'),
        ('moderator', 'Moderator'),
        ('admin', 'Administrator'),
    )

    bio = models.TextField('Биография', blank=True)
    role = models.CharField('Роль', choices=ROLE_CHOICES, default='user', max_length=20)
    confirmation_code = models.CharField('Confirmation Code', max_length=100, blank=True, null=True)

    username = models.CharField('Имя пользователя', max_length=150, unique=True)
    email = models.EmailField('Email адрес', max_length=254, unique=True, blank=False, null=False)
