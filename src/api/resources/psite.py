from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseBadRequest, StreamingHttpResponse
from django.utils.text import get_valid_filename
from rest_framework.decorators import list_route
from base import (
    BaseAPIFilterSet,
    BaseProjectApiViewSet,
    BaseAPISerializer,
)
from mixins import ProtectedResourceMixin
from ..models import Site, Project
from ..reports import RawCSVReport
from ..report_serializer import *


class PSiteSerializer(BaseAPISerializer):
    class Meta:
        geo_field = "location"
        model = Site
        exclude = []


class PSiteReportSerializer(ReportSerializer):
    fields = [
        ReportField("name", "Name"),
        ReportField("location", "Latitude", to_latitude),
        ReportField("location", "Longitude", to_longitude),
        ReportField("country__name", "Country"),
        ReportField("reef_type__name", "Reef type"),
        ReportField("reef_zone__name", "Reef zone"),
        ReportField("exposure__name", "Reef exposure"),
        ReportField("exposure__val", "Reef exposure value"),
        ReportField("notes", "Notes"),
    ]

    class Meta:
        model = Site


class PSiteFilterSet(BaseAPIFilterSet):
    class Meta:
        model = Site
        fields = ["public", "country", "reef_type", "reef_zone", "exposure"]


class PSiteViewSet(ProtectedResourceMixin, BaseProjectApiViewSet):
    model_display_name = "Site"
    serializer_class = PSiteSerializer
    queryset = Site.objects.all()
    project_lookup = "project"
    filter_class = PSiteFilterSet
    search_fields = ["name"]

    @list_route(methods=["get"])
    def fieldreport(self, request, *args, **kwargs):
        try:
            project = Project.objects.get(pk=kwargs['project_pk'])
        except ObjectDoesNotExist:
            return HttpResponseBadRequest('Project doesn\'t exist')
        self.limit_to_project(self, request, *args, **kwargs)

        report = RawCSVReport()
        stream = report.stream(
            self.get_queryset(),
            serializer_class=PSiteReportSerializer)
        response = StreamingHttpResponse(stream, content_type='text/csv')
        ts = datetime.utcnow().strftime("%Y%m%d")
        projname = get_valid_filename(project.name)[:100]
        response['Content-Disposition'] = \
            'attachment; filename="sites-%s-%s.csv"' % (projname, ts)
        return response