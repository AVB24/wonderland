# Generated by Django 2.2.1 on 2019-06-10 20:40

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('records', '0022_auto_20190610_1540'),
    ]

    operations = [
        migrations.AddField(
            model_name='lap',
            name='key',
            field=models.CharField(default=datetime.datetime(2019, 6, 10, 20, 40, 34, 525112, tzinfo=utc), max_length=255, unique=True),
            preserve_default=False,
        ),
    ]
