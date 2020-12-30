# Generated by Django 3.0.3 on 2020-02-29 09:18

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('video', '0012_auto_20200229_0821'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='watched_videos',
            field=models.ManyToManyField(related_name='watched_videos', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='request',
            name='promo_code',
            field=models.CharField(blank=True, max_length=40),
        ),
    ]
