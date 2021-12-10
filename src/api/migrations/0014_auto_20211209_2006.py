# Generated by Django 2.2.24 on 2021-12-09 20:06

import django.contrib.gis.db.models.fields
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0013_auto_20211108_1346'),
    ]

    operations = [
        migrations.CreateModel(
            name='SummarySiteSQLModel',
            fields=[
                ('site_id', models.UUIDField(primary_key=True, serialize=False)),
                ('site_name', models.CharField(max_length=255)),
                ('site_notes', models.TextField(blank=True)),
                ('location', django.contrib.gis.db.models.fields.PointField(srid=4326)),
                ('project_id', models.UUIDField()),
                ('project_name', models.CharField(max_length=255)),
                ('project_status', models.PositiveSmallIntegerField(choices=[(90, 'open'), (80, 'test'), (10, 'locked')], default=90)),
                ('project_notes', models.TextField(blank=True)),
                ('contact_link', models.CharField(max_length=255)),
                ('tags', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('country_id', models.UUIDField()),
                ('country_name', models.CharField(max_length=50)),
                ('reef_type', models.CharField(max_length=50)),
                ('reef_zone', models.CharField(max_length=50)),
                ('reef_exposure', models.CharField(max_length=50)),
                ('project_admins', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('date_min', models.DateField(blank=True, null=True)),
                ('date_max', models.DateField(blank=True, null=True)),
                ('management_regimes', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('protocols', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('data_policy_beltfish', models.CharField(max_length=50)),
                ('data_policy_benthiclit', models.CharField(max_length=50)),
                ('data_policy_benthicpit', models.CharField(max_length=50)),
                ('data_policy_habitatcomplexity', models.CharField(max_length=50)),
                ('data_policy_bleachingqc', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'summary_site_sql',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='SummarySiteModel',
            fields=[
                ('site_id', models.UUIDField(primary_key=True, serialize=False)),
                ('site_name', models.CharField(max_length=255)),
                ('site_notes', models.TextField(blank=True)),
                ('location', django.contrib.gis.db.models.fields.PointField(srid=4326)),
                ('project_id', models.UUIDField()),
                ('project_name', models.CharField(max_length=255)),
                ('project_status', models.PositiveSmallIntegerField(choices=[(90, 'open'), (80, 'test'), (10, 'locked')], default=90)),
                ('project_notes', models.TextField(blank=True)),
                ('contact_link', models.CharField(max_length=255)),
                ('tags', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('country_id', models.UUIDField()),
                ('country_name', models.CharField(max_length=50)),
                ('reef_type', models.CharField(max_length=50)),
                ('reef_zone', models.CharField(max_length=50)),
                ('reef_exposure', models.CharField(max_length=50)),
                ('project_admins', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('date_min', models.DateField(blank=True, null=True)),
                ('date_max', models.DateField(blank=True, null=True)),
                ('management_regimes', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('protocols', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('data_policy_beltfish', models.CharField(max_length=50)),
                ('data_policy_benthiclit', models.CharField(max_length=50)),
                ('data_policy_benthicpit', models.CharField(max_length=50)),
                ('data_policy_habitatcomplexity', models.CharField(max_length=50)),
                ('data_policy_bleachingqc', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'summary_site',
            },
        ),
        migrations.DeleteModel(
            name='SummarySiteViewModel',
        ),
    ]
