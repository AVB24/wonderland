# Generated by Django 2.2.1 on 2019-06-11 19:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('util', '0005_customdocument'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customdocument',
            name='event',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='customdocument',
            name='group',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='customdocument',
            name='region',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
