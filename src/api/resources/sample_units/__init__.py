import uuid
from datetime import datetime
import StringIO
import zipfile


from collections import defaultdict, Iterable
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _
from django.utils.text import get_valid_filename
from django.http import (
    HttpResponse,
    StreamingHttpResponse,
    HttpResponseBadRequest,
)
from ...models import Project, Management, Observer
from ...resources.management import get_rules
from ...reports import RawCSVReport
from ...report_serializer import *


def to_governance(field, row, serializer_instance):
    transect_method = serializer_instance.transect_method or None
    sample_event_path = serializer_instance.sample_event_path or None
    if transect_method is None or sample_event_path is None:
        return ""
    parties = ""
    project_pk = row.get("{}__site__project_id".format(sample_event_path))
    management_id = row.get("{}__management_id".format(sample_event_path))
    lookup = serializer_instance.serializer_cache.get(
        "{}_lookups-management_parties-{}".format(transect_method, project_pk)
    )
    if lookup:
        parties = lookup.get(str(management_id))
    else:
        management = Management.objects.get_or_none(id=management_id)
        if management is not None:
            mps = management.parties.all().iterator()
            parties = ",".join([mp.name for mp in mps])
    return parties


def to_management_rules(field, row, serializer_instance):
    transect_method = serializer_instance.transect_method or None
    sample_event_path = serializer_instance.sample_event_path or None
    if transect_method is None or sample_event_path is None:
        return ""
    project_pk = row.get("{}__site__project_id".format(sample_event_path))
    management_id = row.get("{}__management_id".format(sample_event_path))
    lookup = serializer_instance.serializer_cache.get(
        "{}_lookups-management_rules-{}".format(transect_method, project_pk)
    )
    if lookup:
        return lookup.get(str(management_id))

    return get_rules(Management.objects.get_or_none(id=management_id))


def to_observers(field, row, serializer_instance):
    transect_method = serializer_instance.transect_method or None
    sample_event_path = serializer_instance.sample_event_path or None
    tid = row.get("{}_id".format(transect_method))
    if tid is None or transect_method is None or sample_event_path is None:
        return ""

    project_pk = row.get("{}__site__project_id".format(sample_event_path))
    lookup = serializer_instance.serializer_cache.get(
        "{}_lookups-observers-{}".format(transect_method, project_pk)
    )
    if lookup:
        observers = lookup.get(str(tid))
    else:
        transect = serializer_instance.Meta.model.objects.get_or_none(id=tid)
        if transect is None:
            return ""

        observers = [o.profile_name for o in transect.observers.all().iterator()]
    return ",".join(observers)


class SampleEventReportSerializerMeta(type):
    def __new__(mcs, clsname, bases, dct):
        sample_event_path = dct.get("sample_event_path")
        dct["fields"] = [
            ReportField(
                "{}__site__project__name".format(sample_event_path), "Project name"
            ),
            ReportField("{}__site__country__name".format(sample_event_path), "Country"),
            ReportField("{}__site__name".format(sample_event_path), "Site"),
            ReportField(
                "{}__site__location".format(sample_event_path), "Latitude", to_latitude
            ),
            ReportField(
                "{}__site__location".format(sample_event_path),
                "Longitude",
                to_longitude,
            ),
            ReportField(
                "{}__site__exposure__name".format(sample_event_path), "Exposure"
            ),
            ReportField(
                "{}__site__reef_type__name".format(sample_event_path), "Reef type"
            ),
            ReportField(
                "{}__site__reef_zone__name".format(sample_event_path), "Reef zone"
            ),
            ReportField(
                "{}__sample_date".format(sample_event_path), "Date", to_unicode
            ),
            ReportField(
                "{}__sample_time".format(sample_event_path), "Start time", to_unicode
            ),
            ReportField("{}__tide__name".format(sample_event_path), "Tide"),
            ReportField("{}__visibility__name".format(sample_event_path), "Visibility"),
            ReportField("{}__current__name".format(sample_event_path), "Current"),
            ReportField("{}__depth".format(sample_event_path), "Depth", to_float),
            ReportField(
                "{}__management__name".format(sample_event_path), "Management name"
            ),
            ReportField(
                "{}__management__name_secondary".format(sample_event_path),
                "Management secondary name",
            ),
            ReportField(
                "{}__management__est_year".format(sample_event_path),
                "Management year established",
            ),
            ReportField(
                "{}__management__size".format(sample_event_path),
                "Management size",
                to_float,
            ),
            ReportMethodField("Governance", to_governance),
            ReportField(
                "{}__management__compliance__name".format(sample_event_path),
                "Estimated compliance",
            ),
            ReportMethodField("Management rules", to_management_rules),
            ReportMethodField("Observer", to_observers),
            ReportField("{}__site__notes".format(sample_event_path), "Site notes"),
            ReportField("{}__notes".format(sample_event_path), "Sampling event notes"),
            ReportField(
                "{}__management__notes".format(sample_event_path), "Management notes"
            ),
        ]

        obs_fields = dct.get("obs_fields")
        if obs_fields:
            for f in obs_fields:
                dct["fields"].insert(f[0], f[1])

        return super(SampleEventReportSerializerMeta, mcs).__new__(
            mcs, clsname, bases, dct
        )


class SampleEventReportSerializer(ReportSerializer):
    serializer_cache = dict()
    transect_method = None
    sample_event_path = None

    def preserialize(self, queryset=None):
        self.serializer_cache = dict()
        try:
            values = (
                queryset.values_list(
                    "{}__site__project_id".format(self.sample_event_path), flat=True
                )
                or []
            )
            if not values:
                raise ObjectDoesNotExist
            project_pk = values[0]
        except ObjectDoesNotExist:
            return

        # Observers
        kwargs = {
            "transectmethod__{}__site__project_id".format(
                self.sample_event_path
            ): project_pk
        }
        observers = (
            Observer.objects.select_related("transectmethod")
            .filter(**kwargs)
            .iterator()
        )
        observer_lookup = defaultdict(list)
        for o in observers:
            observer_lookup[str(o.transectmethod.id)].append(o.profile.full_name)
        if len(observer_lookup.keys()) > 0:
            self.serializer_cache[
                "{}_lookups-observers-{}".format(self.transect_method, project_pk)
            ] = observer_lookup

        # Management Parties and Rules
        management_parties_lookup = dict()
        management_rules_lookup = dict()
        for m in Management.objects.filter(project_id=project_pk):
            parties = m.parties.all().order_by("name").values_list("name", flat=True)
            management_parties_lookup[str(m.id)] = ",".join(parties)
            management_rules_lookup[str(m.id)] = get_rules(m)

        if len(management_parties_lookup.keys()) > 0:
            self.serializer_cache[
                "{}_lookups-management_parties-{}".format(
                    self.transect_method, project_pk
                )
            ] = management_parties_lookup
            self.serializer_cache[
                "{}_lookups-management_rules-{}".format(
                    self.transect_method, project_pk
                )
            ] = management_rules_lookup


def save_one_to_many(foreign_key, database_records, data, serializer_class, context):
    model_class = serializer_class.Meta.model
    invalid_count = 0
    errors = []

    # Check for deleted records
    # Fetch existing records in database and see
    # if they exist in request.data
    delete_lookup = [o["id"] for o in data if "id" in o and o["id"] is not None]
    for db_record in database_records:
        if db_record.id not in delete_lookup:
            db_record.delete()

    for data_rec in data:
        rec_id = data_rec.get("id")
        fk = data_rec.get(foreign_key[0])
        # If any new records don't have FK, fill it
        if fk is None:
            data_rec[foreign_key[0]] = foreign_key[1]

        # Create new record
        if rec_id is None:
            data_rec["id"] = uuid.uuid4()
            serializer = serializer_class(data=data_rec, context=context)
        else:
            try:
                # Update existing record
                instance = model_class.objects.get(id=rec_id)
                serializer = serializer_class(instance, data=data_rec, context=context)
            except ObjectDoesNotExist:
                # Id provided but new record
                serializer = serializer_class(data=data_rec, context=context)

        if serializer.is_valid() is False:
            errors.append(serializer.errors)
            invalid_count += 1
            continue

        serializer.save()

    return invalid_count == 0, errors


def save_model(data, serializer_class, context):
    model_class = serializer_class.Meta.model
    instance_id = data.get("id")
    instance = model_class.objects.get_or_none(id=instance_id)
    if instance is None:
        return False, [_("Does not exist")]
    else:
        serializer = serializer_class(instance, data=data, context=context)
        if serializer.is_valid() is False:
            return False, serializer.errors

    serializer.save()
    return True, None


def _set_to_list(obj):
    if isinstance(obj, Iterable):
        return obj
    return [obj]


def fieldreport(obj, request, *args, **kwargs):
    serializer_class = kwargs.get("serializer_class")
    model_cls = kwargs.get("model_cls")
    fk = kwargs.get("fk")
    order_by = kwargs.get("order_by")

    try:
        project = Project.objects.get(pk=kwargs["project_pk"])
    except ObjectDoesNotExist:
        return HttpResponseBadRequest("Project doesn't exist")

    serializer_class = _set_to_list(serializer_class)
    model_cls = _set_to_list(model_cls)

    if len(serializer_class) != len(model_cls):
        raise ValueError("Number of serializer_class and model_cls do not match")

    obj.limit_to_project(request, *args, **kwargs)
    qs = obj.get_queryset()

    streams = []
    for sc, mdl in zip(serializer_class, model_cls):
        transect_ids = [rec.id for rec in obj.filter_queryset(qs).iterator()]
        obls = mdl.objects.filter(**{"%s__in" % fk: transect_ids})
        report = RawCSVReport()
        streams.append(report.stream(obls, serializer_class=sc, order_by=order_by))

    ts = datetime.utcnow().strftime("%Y%m%d")
    projname = get_valid_filename(project.name)[:100]
    if len(streams) == 1:
        response = StreamingHttpResponse(streams[0], content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="%s-%s-%s.csv"' % (
            fk,
            projname,
            ts,
        )
    else:
        inmem_file = StringIO.StringIO()
        zipped_reports = zipfile.ZipFile(
            inmem_file, "w", compression=zipfile.ZIP_DEFLATED
        )

        for mdl, stream in zip(model_cls, streams):
            file_name = "{}-{}-{}.csv".format(
                projname, mdl.__name__.lower(), ts
            )
            content = "".join(list(stream))
            zipped_reports.writestr(file_name, content)
        zipped_reports.close()
        inmem_file.seek(0)
        response = HttpResponse(
            inmem_file.read(), content_type="application/octet-stream"
        )
        response["Content-Disposition"] = 'attachment; filename="%s-%s-%s.zip"' % (
            fk,
            projname,
            ts,
        )

    return response