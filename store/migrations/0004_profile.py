# Generated by Django 4.1.7 on 2023-03-01 23:30

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('store', '0003_rename_phone_number_account_freelancer_key'),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bio', models.CharField(default='Hi my name is ... ', max_length=355)),
                ('user_image', models.ImageField(default='default.png', upload_to='media', validators=[django.core.validators.FileExtensionValidator(['png', 'jpg'])])),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
