# Generated by Django 3.2 on 2023-12-16 13:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0022_auto_20231216_1649'),
    ]

    operations = [
        migrations.AlterField(
            model_name='title',
            name='rating',
            field=models.IntegerField(default=1),
        ),
    ]
