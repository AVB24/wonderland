# Generated by Django 2.2.1 on 2019-06-10 21:05

from django.db import migrations, models
import records.models


class Migration(migrations.Migration):

    dependencies = [
        ('records', '0024_auto_20190610_1702'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lap',
            name='key',
            field=models.CharField(default='', editable=False, max_length=255),
        ),
    ]
