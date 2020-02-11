# Generated by Django 2.2.6 on 2020-02-11 04:28

import django.contrib.gis.db.models.fields
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_auto_20191112_1919'),
    ]

    operations = [
        migrations.AddField(
            model_name='region',
            name='area_of_interest',
            field=django.contrib.gis.db.models.fields.MultiPolygonField(default='MULTIPOLYGON(((0 0,0 0,0 0,0 0,0 0)))', srid=4326),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='belttransectwidthcondition',
            name='size',
            field=models.DecimalField(blank=True, decimal_places=1, max_digits=5, null=True, verbose_name='fish size (cm)'),
        ),
        migrations.AlterField(
            model_name='management',
            name='est_year',
            field=models.PositiveSmallIntegerField(blank=True, null=True, validators=[django.core.validators.MaxValueValidator(2020)], verbose_name='year established'),
        ),
        migrations.AlterField(
            model_name='mpa',
            name='est_year',
            field=models.PositiveSmallIntegerField(blank=True, null=True, validators=[django.core.validators.MaxValueValidator(2020)], verbose_name='year established'),
        ),
    ]
