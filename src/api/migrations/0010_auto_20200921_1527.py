# Generated by Django 2.2.12 on 2020-09-21 15:27

from django.db import migrations

from ..models.view_models import model_view_migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_project_data'),
    ]

    operations = [
        migrations.RunSQL(model_view_migrations.forward_sql(), model_view_migrations.reverse_sql()),
    ]