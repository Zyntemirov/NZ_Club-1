# Generated by Django 3.0.3 on 2020-03-10 10:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('video', '0017_auto_20200310_0955'),
    ]

    operations = [
        migrations.AlterField(
            model_name='video',
            name='facebook',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Файсбук'),
        ),
        migrations.AlterField(
            model_name='video',
            name='instagram',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Инстаграм'),
        ),
        migrations.AlterField(
            model_name='video',
            name='web_site',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Вебсайт'),
        ),
    ]
