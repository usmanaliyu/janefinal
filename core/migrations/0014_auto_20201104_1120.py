# Generated by Django 2.2 on 2020-11-04 11:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_auto_20201104_1118'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='state',
            field=models.CharField(max_length=120, null=True),
        ),
        migrations.AlterField(
            model_name='address',
            name='zip',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]