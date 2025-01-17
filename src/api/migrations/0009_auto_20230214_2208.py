# Generated by Django 3.2.17 on 2023-02-14 22:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_beltfishobsmodel_beltfishsemodel_beltfishsumodel_benthiclitobsmodel_benthiclitsemodel_benthiclitsumo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bleachingqcquadratbenthicpercentobsmodel',
            name='percent_algae',
            field=models.PositiveSmallIntegerField(blank=True, default=0, null=True, verbose_name='macroalgae, % cover'),
        ),
        migrations.AlterField(
            model_name='bleachingqcquadratbenthicpercentobsmodel',
            name='percent_hard',
            field=models.PositiveSmallIntegerField(blank=True, default=0, null=True, verbose_name='hard coral, % cover'),
        ),
        migrations.AlterField(
            model_name='bleachingqcquadratbenthicpercentobsmodel',
            name='percent_soft',
            field=models.PositiveSmallIntegerField(blank=True, default=0, null=True, verbose_name='soft coral, % cover'),
        ),
        migrations.AlterField(
            model_name='bleachingqcsemodel',
            name='percent_algae_avg_avg',
            field=models.DecimalField(blank=True, decimal_places=1, max_digits=4, null=True),
        ),
        migrations.AlterField(
            model_name='bleachingqcsemodel',
            name='percent_hard_avg_avg',
            field=models.DecimalField(blank=True, decimal_places=1, max_digits=4, null=True),
        ),
        migrations.AlterField(
            model_name='bleachingqcsemodel',
            name='percent_soft_avg_avg',
            field=models.DecimalField(blank=True, decimal_places=1, max_digits=4, null=True),
        ),
        migrations.AlterField(
            model_name='bleachingqcsumodel',
            name='percent_algae_avg',
            field=models.DecimalField(blank=True, decimal_places=1, default=0, max_digits=4, null=True),
        ),
        migrations.AlterField(
            model_name='bleachingqcsumodel',
            name='percent_hard_avg',
            field=models.DecimalField(blank=True, decimal_places=1, default=0, max_digits=4, null=True),
        ),
        migrations.AlterField(
            model_name='bleachingqcsumodel',
            name='percent_soft_avg',
            field=models.DecimalField(blank=True, decimal_places=1, default=0, max_digits=4, null=True),
        ),
    ]
