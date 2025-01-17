import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from zipfile import ZIP_DEFLATED, ZipFile

import pytz
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError, Q
from django.http import FileResponse
from django.http.response import HttpResponse, HttpResponseBadRequest
from django.template.defaultfilters import pluralize
from django.utils.dateparse import parse_datetime
from rest_framework import status
from rest_framework import exceptions
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.decorators import action

from ..exceptions import check_uuid
from ..models import ArchivedRecord, Project
from ..notifications import notify_cr_owners_site_mr_deleted
from ..permissions import ProjectDataAdminPermission
from ..utils import create_iso_date_string, get_protected_related_objects
from ..utils.project import get_safe_project_name
from ..utils.sample_unit_methods import edit_transect_method


class ProtectedResourceMixin(object):
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ProtectedError as pe:
            protected_instances = list(get_protected_related_objects(instance))
            num_protected_instances = len(protected_instances)
            protected_instance_displays = [str(pi) for pi in protected_instances]

            model_name = (
                self.model_display_name or self.queryset.model.__class__.__name__
            )
            msg = "Cannot delete '{}' because " "it is referenced by {} {}.".format(
                model_name,
                num_protected_instances,
                pluralize(num_protected_instances, "record,records"),
            )

            msg += " [" + ", ".join(protected_instance_displays) + "]"
            return Response(msg, status=status.HTTP_403_FORBIDDEN)


class NotifyDeletedSiteMRMixin(ProtectedResourceMixin):
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        deleted_by = getattr(request.user, "profile", None)
        response = super().destroy(request, *args, **kwargs)
        notify_cr_owners_site_mr_deleted(instance, deleted_by)
        return response


class CreateOrUpdateSerializerMixin(object):
    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except IntegrityError as err:
            if "violates unique constraint" in str(err).lower():
                ModelClass = self.Meta.model
                instance = ModelClass.objects.get(id=validated_data["id"])
                return self.update(instance, validated_data)
            raise


class UpdatesMixin(object):
    def compress(self, added, modified, removed):
        added_lookup = {str(a["id"]): ts for ts, a in added}
        modified_lookup = {str(m["id"]): ts for ts, m in modified}
        removed_lookup = {str(r["id"]): ts for ts, r in removed}

        compressed_added = []
        for rec_timestamp, rec in added:
            pk = str(rec["id"])
            if pk in removed_lookup and rec_timestamp <= removed_lookup[pk]:
                continue
            compressed_added.append(rec)

        compressed_modified = []
        for rec_timestamp, rec in modified:
            pk = str(rec["id"])
            if pk in added_lookup or (
                pk in removed_lookup and rec_timestamp <= removed_lookup[pk]
            ):
                continue
            compressed_modified.append(rec)

        compressed_removed = []
        for rec_timestamp, rec in removed:
            pk = str(rec["id"])
            if (pk in added_lookup and rec_timestamp < added_lookup[pk]) or (
                pk in modified_lookup and rec_timestamp < modified_lookup[pk]
            ):
                continue
            compressed_removed.append(rec)

        return compressed_added, compressed_modified, compressed_removed

    def apply_query_param(self, query_params, key, value):
        if value is not None:
            query_params[key] = value

    def get_update_timestamp(self, request):
        qp_timestamp = request.query_params.get("timestamp")
        if qp_timestamp is None:
            return HttpResponseBadRequest()

        try:
            timestamp = parse_datetime(qp_timestamp)
        except ValueError:
            timestamp = None

        if timestamp:
            timestamp = timestamp.replace(tzinfo=pytz.utc)

        return timestamp

    def get_updates(self, request, *args, **kwargs):
        timestamp = self.get_update_timestamp(request)
        pk = request.query_params.get("pk")

        serializer = self.get_serializer_class()

        added_filter = dict()
        updated_filter = dict()
        removed_filter = dict(app_label="api")

        self.apply_query_param(added_filter, "created_on__gte", timestamp)
        self.apply_query_param(updated_filter, "created_on__lt", timestamp)
        self.apply_query_param(updated_filter, "updated_on__gt", timestamp)
        self.apply_query_param(removed_filter, "created_on__gte", timestamp)

        self.apply_query_param(added_filter, "pk", pk)
        self.apply_query_param(updated_filter, "pk", pk)
        self.apply_query_param(removed_filter, "record_pk", pk)

        if hasattr(self, "limit_to_project"):
            qry = self.limit_to_project(request, *args, **kwargs)
        else:
            qry = self.filter_queryset(self.get_queryset())

        if hasattr(qry, "model"):
            removed_filter["model"] = qry.model._meta.model_name

        context = {"request": self.request}
        added_records = qry.filter(**added_filter)
        serialized_recs = serializer(added_records, many=True, context=context).data
        added = [(parse_datetime(sr["updated_on"]), sr) for sr in serialized_recs]

        modified_recs = qry.filter(**updated_filter)
        serialized_recs = serializer(modified_recs, many=True, context=context).data
        modified = [(parse_datetime(sr["updated_on"]), sr) for sr in serialized_recs]

        removed = [
            (ar.created_on, dict(id=ar.record_pk, timestamp=ar.created_on))
            for ar in ArchivedRecord.objects.filter(**removed_filter)
        ]

        return added, modified, removed

    @action(detail=False, methods=["GET"])
    def updates(self, request, *args, **kwargs):
        added, modified, removed = self.get_updates(request, *args, **kwargs)
        added, modified, removed = self.compress(added, modified, removed)
        return Response(dict(added=added, modified=modified, removed=removed))


# Use this to override DRF DEFAULT_AUTHENTICATION_CLASSES (in settings) from ViewSet for specific methods
# Avoids 401s for unprotected endpoints -- but 403s (permissions classes) unaffected
class MethodAuthenticationMixin(object):
    # method_authentication_classes = {
    #     "OPTIONS": None,
    #     "GET": None,
    #     "POST": None,
    #     "PUT": None,
    #     "PATCH": None,
    #     "HEAD": None,
    #     "DELETE": None,
    #     "TRACE": None,
    #     "CONNECT": None,
    # }

    def initialize_request(self, request, *args, **kwargs):
        parser_context = self.get_parser_context(request)

        method = request.method.upper()
        if hasattr(self, "method_authentication_classes") and isinstance(
            self.method_authentication_classes.get(method), (list, tuple)
        ):
            authenticators = [
                auth() for auth in self.method_authentication_classes[method]
            ]
        else:
            authenticators = self.get_authenticators()

        return Request(
            request,
            parsers=self.get_parsers(),
            authenticators=authenticators,
            negotiator=self.get_content_negotiator(),
            parser_context=parser_context,
        )


class OrFilterSetMixin(object):
    def str_or_lookup(self, queryset, name, value, key=None, lookup_expr="iexact"):
        if not isinstance(name, (list, set, tuple)):
            name = [name]
        q = Q()
        for n in name:
            fieldname = "{}__{}".format(n, lookup_expr)
            for v in set(value):
                if v is not None and v != "":
                    predicate = {fieldname: str(v).strip()}
                    if key is not None:
                        predicate = {fieldname: [{key: str(v).strip()}]}
                    q |= Q(**predicate)

        return queryset.filter(q).distinct()

    def id_lookup(self, queryset, name, value):
        return self.str_or_lookup(queryset, name, value)

    def char_lookup(self, queryset, name, value):
        return self.str_or_lookup(queryset, name, value, lookup_expr="icontains")

    def json_id_lookup(self, queryset, name, value):
        return self.str_or_lookup(queryset, name, value, "id", "contains")

    def json_name_lookup(self, queryset, name, value):
        return self.str_or_lookup(queryset, name, value, "name", "contains")


class SampleUnitMethodEditMixin(object):
    @transaction.atomic
    @action(
        detail=True, methods=["PUT"], permission_classes=[ProjectDataAdminPermission]
    )
    def edit(self, request, project_pk, pk):
        collect_record_owner = Project.objects.get_or_none(id=request.data.get("owner"))
        if collect_record_owner is None:
            collect_record_owner = request.user.profile

        try:
            model = self.get_queryset().model
            if hasattr(model, "protocol") is False:
                raise ValueError("Unsupported model")

            collect_record = edit_transect_method(
                self.serializer_class,
                collect_record_owner,
                request,
                pk,
                model.protocol
            )
            return Response({"id": str(collect_record.pk)})
        except Exception as err:
            print(err)
            return Response(str(err), status=500)


class SampleUnitMethodSummaryReport(object):
    @action(
        detail=False, methods=["GET"], permission_classes=[ProjectDataAdminPermission]
    )
    def xlsx(self, request, project_pk):
        from ..utils.reports import create_sample_unit_method_summary_report
        try:
            model = self.get_queryset().model
            with NamedTemporaryFile(delete=False) as f:
                try:
                    protocol = getattr(model, "protocol")
                    create_sample_unit_method_summary_report(
                        project_pk,
                        protocol,
                        f.name,
                        request=request
                    )
                except AttributeError as ae:
                    raise exceptions.ValidationError("Uknown protocol") from ae
                except ValueError as ve:
                    raise exceptions.ValidationError(f"{protocol} protocol not suppoort") from ve
                
                try:
                    base_file_name = f"{get_safe_project_name(project_pk)}_{protocol}_{create_iso_date_string(delimiter='_')}"
                    xlsx_file_name = f"{base_file_name}.xlsx"
                    zip_file_name = f"{base_file_name}.zip"
                except ValueError as e:
                    raise exceptions.ValidationError(f"[{project_pk}] Project does not exist") from e
                
                try:
                    with ZipFile(zip_file_name, "w", compression=ZIP_DEFLATED) as z:
                        z.write(f.name, arcname=xlsx_file_name)

                    z_file = open(zip_file_name, "rb")
                    response = FileResponse(z_file, content_type="application/zip")
                    response["Content-Length"] = os.fstat(z_file.fileno()).st_size
                    response["Content-Disposition"] = f'attachment; filename="{zip_file_name}"'

                    return response
                finally:
                    if zip_file_name and Path(zip_file_name).exists():
                        os.remove(zip_file_name)
        except Exception as err:
            print(err)
            return Response(str(err), status=500)


class CopyRecordsMixin:
    @action(
        detail=False,
        methods=["post"],
    )
    def copy(self, request, project_pk, *args, **kwargs):
        """
        Payload schema:
        
        {
            "original_ids": [Array] Original record ids to copy to project.
        }

        """
        
        profile = request.user.profile
        context = {"request": request}
        data = request.data
        original_ids = data.get("original_ids") or []
        save_point_id = transaction.savepoint()

        new_records = []
        for original_id in original_ids:
            check_uuid(original_id)
            try:
                new_record = self.get_queryset().model.objects.get_or_none(id=original_id)
                if new_record is None:
                    transaction.savepoint_rollback(save_point_id)
                    raise exceptions.ValidationError(f"Original id does not exist [{original_id}]")

                new_record.id = None
                new_record.project_id = project_pk
                new_record.created_by = profile
                new_record.save()

                record_serializer = self.serializer_class(instance=new_record, context=context)
                new_records.append(record_serializer.data)
            except Exception as err:
                print(err)
                transaction.savepoint_rollback(save_point_id)
                raise exceptions.APIException(detail=f"[{type(err).__name__}] Copy records") from err

        transaction.savepoint_commit(save_point_id)
        return Response(new_records)
