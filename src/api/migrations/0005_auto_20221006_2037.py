# Generated by Django 3.2.15 on 2022-10-06 20:37

from django.db import migrations


def fix_mono(apps, schema_editor):
    FishFamily = apps.get_model("api", "FishFamily")
    FishGenus = apps.get_model("api", "FishGenus")

    try:
        correct_family = FishFamily.objects.get(name="Monacanthidae")
        incorrect_family = FishFamily.objects.get(name="Monocanthidae")
        if correct_family and incorrect_family:
            genera_to_reassign = FishGenus.objects.filter(family=incorrect_family)
            genera_to_reassign.update(family=correct_family)
            incorrect_family.delete()
    except (FishFamily.DoesNotExist, FishGenus.DoesNotExist):
        pass


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_merge_0003_auto_20220818_1823_0003_auto_20220823_1042'),
    ]

    operations = [
        migrations.RunPython(fix_mono, migrations.RunPython.noop)
    ]
