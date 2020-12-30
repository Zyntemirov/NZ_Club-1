# Generated by Django 3.0.3 on 2020-02-22 09:54

import datetime
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('video', '0002_auto_20200222_0737'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='image',
            field=models.ImageField(default=datetime.datetime(2020, 2, 22, 9, 54, 12, 272569, tzinfo=utc), upload_to='videos/'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='comment',
            name='reply',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='replies', to='video.Comment'),
        ),
    ]
