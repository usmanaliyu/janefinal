# Generated by Django 2.2.10 on 2021-06-23 03:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='blog',
            name='featured',
            field=models.BooleanField(default=False),
        ),
    ]