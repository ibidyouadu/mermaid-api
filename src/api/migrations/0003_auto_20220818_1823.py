# Generated by Django 2.2.27 on 2022-08-18 18:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_summarysampleeventmodel_sample_event_notes'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mpazone',
            name='management_ptr',
        ),
        migrations.RemoveField(
            model_name='mpazone',
            name='mpa',
        ),
        migrations.DeleteModel(
            name='MPA',
        ),
        migrations.DeleteModel(
            name='MPAZone',
        ),
    ]
