# Generated by Django 2.1.7 on 2020-02-06 08:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('socials', '0008_notification_seen'),
    ]

    operations = [
        migrations.AlterField(
            model_name='channel',
            name='name',
            field=models.CharField(max_length=30),
        ),
    ]
