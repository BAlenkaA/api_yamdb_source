# Generated by Django 3.2 on 2023-12-13 18:07

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0013_auto_20231213_2106'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='pub_date',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='Дата комментария'),
            preserve_default=False,
        ),
    ]