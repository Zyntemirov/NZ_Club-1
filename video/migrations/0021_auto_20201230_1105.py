# Generated by Django 3.0.3 on 2020-12-30 11:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('video', '0020_auto_20200312_1543'),
    ]

    operations = [
        migrations.AlterField(
            model_name='banner',
            name='video',
            field=models.CharField(max_length=255, null=True, verbose_name='Ютуб ссылка'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='video',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='video.Video', verbose_name='Ютуб ссылка'),
        ),
        migrations.AlterField(
            model_name='tariff',
            name='video',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tariffs', to='video.Video', verbose_name='Ютуб ссылка'),
        ),
        migrations.AlterField(
            model_name='video',
            name='video',
            field=models.CharField(max_length=255, null=True, verbose_name='Ютуб ссылка'),
        ),
        migrations.AlterField(
            model_name='videotraining',
            name='video',
            field=models.CharField(max_length=255, null=True, verbose_name='Ютуб ссылка'),
        ),
        migrations.AlterField(
            model_name='viewhistory',
            name='video',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='histories', to='video.Video', verbose_name='Ютуб ссылка'),
        ),
    ]