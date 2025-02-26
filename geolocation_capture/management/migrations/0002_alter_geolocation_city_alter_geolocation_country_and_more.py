# Generated by Django 4.2.7 on 2025-02-18 21:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='geolocation',
            name='city',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='geolocation',
            name='country',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='geolocation',
            name='latitude',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='geolocation',
            name='longitude',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='geolocation',
            name='region',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
