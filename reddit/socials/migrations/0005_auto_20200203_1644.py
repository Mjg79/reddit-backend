# Generated by Django 2.1.7 on 2020-02-03 16:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('socials', '0004_auto_20200203_1630'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='audience_id',
            field=models.IntegerField(verbose_name='audience id'),
        ),
    ]
