# Generated by Django 2.2.6 on 2020-02-08 05:56

import json
import pathlib

from django.contrib.gis.geos import GEOSGeometry
from django.db import migrations

MIGRATIONS_DIR = pathlib.Path(__file__).parent.absolute()


def get_features():
    with open(pathlib.Path.joinpath(MIGRATIONS_DIR, "regions.geojson")) as f:
        region_features = json.load(f)["features"]
        for region_feature in region_features:
            region_name = region_feature["properties"]["name"]
            geom = region_feature["geometry"]
            yield region_name, geom


def load_regions(apps, *args, **kwargs):
    Region = apps.get_model("api", "Region")

    Region.objects.filter(name__in=["Caribbean", "Indo-Pacific"]).delete()

    for region_name, area_of_interest in get_features():
        Region.objects.get_or_create(
            name=region_name,
            area_of_interest=GEOSGeometry(json.dumps(area_of_interest)),
        )


def unload_regions(apps, *args, **kwargs):
    Region = apps.get_model("api", "Region")
    region_names = dict(get_features()).keys()
    Region.objects.filter(name__in=region_names).delete()


class Migration(migrations.Migration):

    dependencies = [("api", "0011_auto_20200211_0428")]

    operations = [migrations.RunPython(load_regions, unload_regions)]
