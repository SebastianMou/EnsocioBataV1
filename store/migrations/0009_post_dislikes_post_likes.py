# Generated by Django 4.1.7 on 2023-03-25 19:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0008_profile_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='dislikes',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='post',
            name='likes',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
