# Generated by Django 3.2 on 2023-12-13 18:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0009_alter_review_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='text',
            field=models.TextField(default=1, verbose_name='Текст отзыва'),
            preserve_default=False,
        ),
    ]
