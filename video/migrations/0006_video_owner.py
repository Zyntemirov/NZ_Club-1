# Generated by Django 3.0.3 on 2020-02-24 07:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('video', '0005_request_is_checked'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='owner',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='users', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
