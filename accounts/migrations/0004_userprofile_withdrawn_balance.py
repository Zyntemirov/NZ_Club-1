# Generated by Django 3.0.3 on 2020-02-26 19:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_auto_20200222_0726'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='withdrawn_balance',
            field=models.FloatField(default=0),
        ),
    ]
