# Generated by Django 2.2.1 on 2019-05-31 20:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('records', '0016_auto_20190531_1656'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lap',
            name='car',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='records.Car'),
        ),
    ]
