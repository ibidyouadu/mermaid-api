# Generated by Django 2.2.12 on 2020-12-14 22:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_auto_20201111_1844'),
    ]

    operations = [
        migrations.AlterField(
            model_name='benthictransect',
            name='sample_time',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='fishbelttransect',
            name='sample_time',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='quadratcollection',
            name='sample_time',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='sampleevent',
            name='sample_time',
            field=models.TimeField(blank=True, null=True),
        ),
    ]