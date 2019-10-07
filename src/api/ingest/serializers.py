# TODO:
# x parse observations
# x parse transect
# x group observations by sample event
# x Serialize observers
# 5. dry up code for other observations
# x write records to db
# 7. Error reporting
# x Mock request
# 9. Validate all records (interval)
# 10. Caching
# x Sorting observations by interval

import uuid
from collections import OrderedDict
from collections.abc import Iterable, Mapping
from operator import itemgetter

from rest_framework import serializers
from rest_framework.fields import empty
from rest_framework.serializers import ListSerializer, Serializer

from .. import utils
from ..decorators import timeit
from ..exceptions import check_uuid
from ..models import BenthicAttribute, Management, Site
from ..resources.choices import ChoiceViewSet
from ..resources.collect_record import CollectRecordSerializer
from ..utils import tokenutils


def build_choices(key, choices):
    return [(str(c["id"]), str(c["name"])) for c in choices[key]["data"]]


class CollectRecordCSVListSerializer(ListSerializer):
    obs_field_identifier = "data__obs_"

    def split_list_fields(self, field_name, data, choices=None):
        val = data.get(field_name, empty)
        if val == empty:
            return

        if choices:
            data[field_name] = [choices.get(s.strip().lower()) for s in val.split(",")]
        else:
            data[field_name] = [s.strip() for s in val.split(",")]

    def map_column_names(self, row):
        header_map = self.child.header_map
        return {
            (header_map[k.strip()] if k.strip() in header_map else k): v
            for k, v in row.items()
        }

    def assign_choices(self, row, choices_sets):
        for name, field in self.child.fields.items():
            val = field.get_value(row)
            choices = choices_sets.get(name)
            if choices is None:
                continue
            try:
                val = self._lower(val)
                row[name] = choices.get(val)
            except (ValueError, TypeError):
                row[name] = None

    def get_sample_event_date(self, row):
        return "{}-{}-{}".format(
            row["data__sample_event__sample_date__year"],
            row["data__sample_event__sample_date__month"],
            row["data__sample_event__sample_date__day"],
        )

    def get_sample_event_time(self, row):
        return row.get("data__sample_event__sample_time") or "00:00:00"

    def remove_extra_data(self, row):
        field_names = set(self.child.fields.keys())
        row_keys = set(row.keys())
        diff_keys = row_keys.difference(field_names)

        for name in diff_keys:
            del row[name]

    def _lower(self, val):
        if isinstance(val, str):
            return val.lower()
        return val

    def _get_reverse_choices(self, field):
        return dict((self._lower(v), k) for k, v in field.choices.items())

    def get_choices_sets(self):
        choices = dict()
        for name, field in self.child.fields.items():
            if hasattr(field, "choices"):
                choices[name] = self._get_reverse_choices(field)
            elif (
                hasattr(self.child, "project_choices")
                and name in self.child.project_choices
            ):
                choices[name] = self.child.project_choices[name]

        return choices

    def sort_records(self, data):
        if (
            hasattr(self.child, "ordering_field") is False
            or self.child.ordering_field is None
        ):
            return data

        group_fields = self.get_group_by_fields()
        group_fields.append(self.child.ordering_field)

        return sorted(data, key=itemgetter(*group_fields))

    def format_data(self, data):
        assert (
            hasattr(self.child, "protocol") and self.child.protocol is not None
        ), "protocol is required serializer property"

        assert (
            hasattr(self.child, "header_map") is True
            or self.child.header_map is not None
        ), "header_map is a required serializer property"

        fmt_rows = []
        choices_sets = self.get_choices_sets()
        protocol = self.child.protocol
        for row in data:
            fmt_row = self.map_column_names(row)
            fmt_row["data__sample_event__sample_date"] = self.get_sample_event_date(
                fmt_row
            )
            fmt_row["data__sample_event__sample_time"] = self.get_sample_event_time(
                fmt_row
            )
            fmt_row["data__protocol"] = protocol

            self.remove_extra_data(fmt_row)
            self.assign_choices(fmt_row, choices_sets)
            self.split_list_fields("data__observers", fmt_row)

            fmt_rows.append(fmt_row)

        sorted_fmt_rows = self.sort_records(fmt_rows)
        return sorted_fmt_rows

    def run_validation(self, data=empty):
        return super().run_validation(data=self.format_data(data))

    @classmethod
    def create_key(cls, record, keys):
        hash = []
        for k in sorted(keys):
            v = utils.get_value(record, k)
            if isinstance(v, list):
                v = ",".join([str(s) for s in sorted(v)])
            elif isinstance(v, dict):
                v = ",".join([str(v[i]) for i in sorted(v)])
            else:
                v = str(v)
            hash.append(v)
        return "::".join(hash)

    def get_group_by_fields(self):
        group_fields = []
        for name, field in self.child.get_fields().items():
            if (
                field.required is True
                and name.startswith(self.obs_field_identifier) is False
            ):
                group_fields.append(name)
        return group_fields

    def group_records(self, records):
        group_fields = self.get_group_by_fields()
        groups = OrderedDict()
        for record in records:
            key = self.create_key(record, group_fields)
            obs = utils.get_value(record, self.child.observations_field)
            if key not in groups:
                utils.set_value(record, self.child.observations_field, value=[obs])
                groups[key] = record
            else:
                utils.get_value(groups[key], self.child.observations_field).append(obs)

        return list(groups.values())

    def create(self, validated_data):
        records = super().create(validated_data)
        output = self.group_records(records)

        crs = CollectRecordSerializer(data=output, context=self.context, many=True)
        if crs.is_valid() is False:
            return None
        else:
            return crs.save()


class CollectRecordCSVSerializer(Serializer):
    protocol = None
    observations_field = None
    header_map = {
        "Site *": "data__sample_event__site",
        "Management *": "data__sample_event__management",
        "Sample date: Year *": "data__sample_event__sample_date__year",
        "Sample date: Month *": "data__sample_event__sample_date__month",
        "Sample date: Day *": "data__sample_event__sample_date__day",
        "Sample time": "data__sample_event__sample_time",
        "Depth *": "data__sample_event__depth",
        "Interval size": "data__interval_size",
        "Visibility": "data__sample_event__visibility",
        "Current": "data__sample_event__current",
        "Relative depth": "data__sample_event__relative_depth",
        "Tide": "data__sample_event__tide",
        "Notes": "data__sample_event__notes",
        "Observer name *": "data__observers",
        "Observation interval *": "data__obs_benthic_pits__interval",
        "Benthic attribute *": "data__obs_benthic_pits__attribute",
        "Growth form *": "data__obs_benthic_pits__growth_form",
    }

    # CHOICES
    _choices = ChoiceViewSet().get_choices()
    visibility_choices = build_choices("visibilities", _choices)
    current_choices = build_choices("currents", _choices)
    relative_depth_choices = build_choices("relativedepths", _choices)
    tide_choices = build_choices("tides", _choices)

    _reverse_choices = {}

    # PROJECT RELATED CHOICES
    project_choices = {
        "data__sample_event__site": None,
        "data__sample_event__management": None,
    }

    # FIELDS
    project = serializers.UUIDField(format="hex_verbose")
    profile = serializers.UUIDField(format="hex_verbose")
    data__protocol = serializers.CharField(required=True, allow_blank=False)

    data__sample_event__site = serializers.CharField()
    data__sample_event__management = serializers.CharField()
    data__sample_event__sample_date = serializers.DateField()
    data__sample_event__sample_time = serializers.TimeField(default="00:00:00")
    data__sample_event__depth = serializers.DecimalField(max_digits=3, decimal_places=1)

    data__sample_event__visibility = serializers.ChoiceField(
        choices=visibility_choices, required=False, allow_null=True, allow_blank=True
    )
    data__sample_event__current = serializers.ChoiceField(
        choices=current_choices, required=False, allow_null=True, allow_blank=True
    )
    data__sample_event__relative_depth = serializers.ChoiceField(
        choices=relative_depth_choices,
        required=False,
        allow_null=True,
        allow_blank=True,
    )
    data__sample_event__tide = serializers.ChoiceField(
        choices=tide_choices, required=False, allow_null=True, allow_blank=True
    )
    data__sample_event__notes = serializers.CharField(required=False, allow_blank=True)

    # data__observers = ProjectProfileSerializer(many=True)
    data__observers = serializers.ListField(
        child=serializers.CharField(), allow_empty=False
    )

    class Meta:
        list_serializer_class = CollectRecordCSVListSerializer

    def __init__(self, data=None, instance=None, project_choices=None, **kwargs):
        if instance is not None:
            raise NotImplementedError("instance argument not implemented")
        if isinstance(data, Mapping):
            self.original_data = data.copy()
        elif isinstance(data, Iterable) and isinstance(data, str) is False:
            self.original_data = [d for d in data]
        else:
            self.original_data = None

        if project_choices:
            self.project_choices = project_choices

        super().__init__(instance=None, data=data, **kwargs)

    def get_initial(self):
        if not isinstance(self._original_data, Mapping):
            return OrderedDict()

        return OrderedDict(
            [
                (field_name, field.get_value(self._original_data))
                for field_name, field in self.fields.items()
                if (field.get_value(self._original_data) == empty)
                and not field.read_only
            ]
        )

    def validate(self, data):
        # Validate common Transect level fields
        return data

    def create_path(self, field_path, node, val):
        path = field_path.pop(0)
        if path not in node:
            if len(field_path) >= 1:
                node[path] = dict()
                self.create_path(field_path, node[path], val)
            else:
                node[path] = val
        else:
            if len(field_path) >= 1:

                self.create_path(field_path, node[path], val)
            else:
                node[path] = val
        return node

    def create(self, validated_data):
        output = validated_data.copy()

        for name, field in self.fields.items():
            field_path = field.field_name.split("__")
            val = validated_data.get(name)
            output = self.create_path(field_path, output, val)
        output["id"] = str(uuid.uuid4())

        # Need to serialize observers after validation to avoid
        # unique id errors
        project_profiles = self.project_choices.get("project_profiles")
        ob_names = output["data"]["observers"]
        output["data"]["observers"] = [
            project_profiles.get(ob_name.lower()) for ob_name in ob_names
        ]

        return output


class BenthicPITCSVSerializer(CollectRecordCSVSerializer):
    protocol = "benthicpit"
    observations_field = "data__obs_benthic_pits"
    ordering_field = "data__obs_benthic_pits__interval"
    header_map = CollectRecordCSVSerializer.header_map
    header_map.update(
        {
            "Interval size *": "data__interval_size",
            "Transect length surveyed *": "data__benthic_transect__len_surveyed",
            "Transect number *": "data__benthic_transect__number",
            "Transect label": "data__benthic_transect__label",
            "Reef Slope": "data__benthic_transect__reef_slope",
        }
    )
    _choices = ChoiceViewSet().get_choices()
    reef_slopes_choices = [
        (str(c["id"]), c["val"]) for c in _choices["reefslopes"]["data"]
    ]
    growth_form_choices = build_choices("growthforms", _choices)
    benthic_attributes_choices = [
        (str(ba.id), ba.name) for ba in BenthicAttribute.objects.all()
    ]

    data__interval_size = serializers.DecimalField(max_digits=4, decimal_places=2)
    data__benthic_transect__len_surveyed = serializers.IntegerField(min_value=0)
    data__benthic_transect__number = serializers.IntegerField(min_value=0)
    data__benthic_transect__label = serializers.CharField(
        allow_blank=True, required=False
    )
    data__benthic_transect__reef_slope = serializers.ChoiceField(
        choices=reef_slopes_choices, required=False, allow_null=True, allow_blank=True
    )

    data__obs_benthic_pits__interval = serializers.DecimalField(
        max_digits=7, decimal_places=2
    )
    data__obs_benthic_pits__attribute = serializers.ChoiceField(
        choices=benthic_attributes_choices
    )
    data__obs_benthic_pits__growth_form = serializers.ChoiceField(
        choices=growth_form_choices, required=False, allow_null=True, allow_blank=True
    )

    # def sort_observations(self, data):
    #     f = itemgetter('data__obs_benthic_pits__interval')
    #     data.sort(key=f)

    # def format_data(self, data):
    #     data = super().format_data()
    #     self.sort_observations(data)
    #     return data
