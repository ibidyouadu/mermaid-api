import uuid
import six
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers, viewsets
from rest_framework.serializers import (
    UUIDField,
    PrimaryKeyRelatedField,
)
from rest_framework.exceptions import MethodNotAllowed, ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from rest_framework.fields import empty
from rest_framework.compat import unicode_to_repr
from rest_framework.decorators import list_route
from rest_condition import Or
from django.core.exceptions import FieldDoesNotExist

from django.db.models.fields.related import ForeignObjectRel
from rest_framework.validators import qs_exists
import django_filters
from django_filters import Filter
from django_filters.fields import Lookup
from django.conf import settings
from ..models import BaseAttributeModel, Tag, APPROVAL_STATUSES
from ..exceptions import check_uuid
from ..permissions import *
from ..utils.auth0utils import get_jwt_token
from ..utils.auth0utils import get_unverified_profile
from .mixins import MethodAuthenticationMixin, UpdatesMixin


def to_tag_model_instances(tags, updated_by):
    """
    Tweaked from taggit/managers.py. Takes an iterable containing either strings, tag objects, or a mixture
    of both and returns set of tag objects.
    """

    str_tags = set()
    tag_objs = set()

    for t in tags:
        if isinstance(t, Tag):
            tag_objs.add(t)
        elif isinstance(t, six.string_types):
            str_tags.add(t)
        else:
            raise ValueError(
                "Cannot add {0} ({1}). Expected {2} or str.".format(
                    t, type(t), Tag))

    case_insensitive = getattr(settings, 'TAGGIT_CASE_INSENSITIVE', False)

    if case_insensitive:
        existing = []
        tags_to_create = []

        for name in str_tags:
            try:
                tag = Tag.objects.get(name__iexact=name)
                existing.append(tag)
            except Tag.DoesNotExist:
                tags_to_create.append(name)
    else:
        existing = Tag.objects.filter(name__in=str_tags)
        tags_to_create = str_tags - {t.name for t in existing}

    tag_objs.update(existing)

    for new_tag in tags_to_create:
        if case_insensitive:
            try:
                tag = Tag.objects.get(name__iexact=new_tag)
            except Tag.DoesNotExist:
                tag = Tag.objects.create(name=new_tag, updated_by=updated_by)
        else:
            tag = Tag.objects.create(name=new_tag, updated_by=updated_by)

        tag_objs.add(tag)

    return tag_objs


class ModelNameReadOnlyField(serializers.Field):
    def to_representation(self, obj):
        return u'{}'.format(obj.name)


class ModelValReadOnlyField(serializers.Field):
    def to_representation(self, obj):
        return u'{}'.format(obj.val)


class TagField(serializers.Field):

    def to_representation(self, obj):
        return u'{}'.format(obj.name)

    def to_internal_value(self, data):
        if not isinstance(data, six.text_type):
            msg = 'Incorrect type. Expected a string, but got %s'
            raise ValidationError(msg % type(data).__name__)
        return Tag(name=data)


class StandardResultPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'limit'
    max_page_size = 5000


class CurrentProfileDefault(object):
    def set_context(self, serializer_field):
        token = get_jwt_token(serializer_field.context['request'])
        self.profile = get_unverified_profile(token)

    def __call__(self):
        return self.profile

    def __repr__(self):
        return unicode_to_repr('%s()' % self.__class__.__name__)


class BaseAPISerializer(serializers.ModelSerializer):
    id = UUIDField(allow_null=True)
    updated_by = PrimaryKeyRelatedField(read_only=True,
                                        default=CurrentProfileDefault())

    class Meta:
        available_fields = []
        model = None

    def __init__(self, *args, **kwargs):
        super(BaseAPISerializer, self).__init__(*args, **kwargs)

        request = self.context.get('request')
        if request is None:
            return

        available_fields = getattr(self.Meta, 'available_fields', []) or []
        fields = self.get_fields()
        include_fields_param = request.GET.get('include_fields') or ''
        include_fields = [f.strip() for f in include_fields_param.split(',')]
        exclude_fields = []
        if '__all__' in include_fields_param:
            valid_include_fields = available_fields
        else:
            available_field_set = set(available_fields)
            include_field_set = set(include_fields)

            # Only include additional fields that have been asked for.
            valid_include_fields = include_field_set.intersection(available_field_set)
            # Any additional fields that haven't been asked for ensure they
            # are removed from serializer.
            exclude_fields = available_field_set.difference(valid_include_fields)

        for field in valid_include_fields:
            if field not in available_fields:
                continue
            self.fields[field] = fields.get(field)

        for field in exclude_fields:
            if field in fields:
                self.fields.pop(field)

    def validate_id(self, value):
        message = _('This field must be unique.')

        if value is None:
            return value

        ModelClass = self.Meta.model
        queryset = ModelClass.objects.filter(pk=check_uuid(value))
        existing_instance = getattr(self.fields['id'].parent, 'instance', None)
        if existing_instance is not None:
            queryset = queryset.exclude(pk=self.instance.pk)

        if qs_exists(queryset):
            raise ValidationError(message, code='unique')

        return value

    def save(self, **kwargs):
        token = get_jwt_token(self.context['request'])
        kwargs["updated_by"] = get_unverified_profile(token)
        return super(BaseAPISerializer, self).save(**kwargs)


class SampleEventExtendedSerializer(BaseAPISerializer):
    _sample_event = None

    def __init__(self, *args, **kwargs):
        if self._sample_event is None:
            raise Exception('SampleEventExtendedSerializer must be given a _sample_event string')

        self.fields['project_name'] = serializers.ReadOnlyField(source='{}.site.project.name'.format(self._sample_event))
        self.fields['country_name'] = serializers.ReadOnlyField(source='{}.site.country.name'.format(self._sample_event))
        self.fields['site_name'] = serializers.ReadOnlyField(source='{}.site.name'.format(self._sample_event))
        self.fields['latitude'] = serializers.SerializerMethodField()
        self.fields['longitude'] = serializers.SerializerMethodField()
        self.fields['exposure_name'] = serializers.ReadOnlyField(source='{}.site.exposure.name'.format(self._sample_event))
        self.fields['reef_slope_name'] = serializers.ReadOnlyField(source='{}.reef_slope.name'.format(self._sample_event))
        self.fields['reef_type_name'] = serializers.ReadOnlyField(source='{}.site.reef_type.name'.format(self._sample_event))
        self.fields['reef_zone_name'] = serializers.ReadOnlyField(source='{}.site.reef_zone.name'.format(self._sample_event))
        self.fields['sample_date'] = serializers.ReadOnlyField(source='{}.sample_date'.format(self._sample_event))
        self.fields['sample_time'] = serializers.ReadOnlyField(source='{}.sample_time'.format(self._sample_event))
        self.fields['tide_name'] = serializers.ReadOnlyField(source='{}.tide.name'.format(self._sample_event))
        self.fields['visibility_name'] = serializers.ReadOnlyField(source='{}.visibility.name'.format(self._sample_event))
        self.fields['current_name'] = serializers.ReadOnlyField(source='{}.current.name'.format(self._sample_event))
        self.fields['depth'] = serializers.ReadOnlyField(source='{}.depth'.format(self._sample_event))
        self.fields['management_name'] = serializers.ReadOnlyField(source='{}.management.name'.format(self._sample_event))
        self.fields['management_name_secondary'] = serializers.ReadOnlyField(source='{}.management.name_secondary'.format(self._sample_event))
        self.fields['management_est_year'] = serializers.ReadOnlyField(source='{}.management.est_year'.format(self._sample_event))
        self.fields['management_size'] = serializers.ReadOnlyField(source='{}.management.size'.format(self._sample_event))
        self.fields['management_compliance'] = serializers.ReadOnlyField(source='{}.management.compliance.name'.format(self._sample_event))
        self.fields['management_parties'] = serializers.SerializerMethodField()
        self.fields['management_rules'] = serializers.SerializerMethodField()
        self.fields['observers'] = serializers.SerializerMethodField()
        self.fields['site_notes'] = serializers.ReadOnlyField(source='{}.site.notes'.format(self._sample_event))
        self.fields['sample_event_notes'] = serializers.ReadOnlyField(source='{}.notes'.format(self._sample_event))
        self.fields['management_notes'] = serializers.ReadOnlyField(source='{}.management.notes'.format(self._sample_event))

        super(SampleEventExtendedSerializer, self).__init__(*args, **kwargs)


class ExtendedSerializer(serializers.ModelSerializer):
    def __init__(self, instance=None, data=empty, exclude=[], *args, **kwargs):
        super(ExtendedSerializer, self).__init__(*args, **kwargs)

        for exc in exclude:
            if exc in self.fields:
                del self.fields[exc]


class ListFilter(Filter):
    def filter(self, qs, value):
        value_list = [v.strip() for v in value.split(u',')]
        return super(ListFilter, self).filter(qs, Lookup(value_list, 'in'))


# Return objects that actually are null when user asks for them with 'null'
# Note this can't subclass UUIDFilter because of the additional pattern check (?)
class NullableUUIDFilter(django_filters.CharFilter):

    def filter(self, qs, value):
        if value != settings.API_NULLQUERY:
            if isinstance(value, uuid.UUID):
                return value.hex
            return super(NullableUUIDFilter, self).filter(qs, value)

        qs = self.get_method(qs)(**{'%s__isnull' % self.name: True})
        return qs.distinct() if self.distinct else qs


class BaseAPIFilterSet(django_filters.FilterSet):
    created_on = django_filters.DateTimeFromToRangeFilter()
    updated_on = django_filters.DateTimeFromToRangeFilter()
    updated_by = django_filters.NumberFilter()

    class Meta:
        fields = ['created_on', 'updated_on', 'updated_by', ]


class RelatedOrderingFilter(OrderingFilter):
    """
    Extends OrderingFilter to support ordering by fields in related models
    using the Django ORM __ notation
    https://github.com/tomchristie/django-rest-framework/issues/1005
    """

    def is_valid_field(self, model, field):
        """
        Return true if the field exists within the model (or in the related
        model specified using the Django ORM __ notation)
        """
        components = field.split('__', 1)
        try:
            field = model._meta.get_field(components[0])

            # reverse relation
            if isinstance(field, ForeignObjectRel):
                return self.is_valid_field(field.related_model, components[1])

            # foreign key
            if field.rel and len(components) == 2:
                return self.is_valid_field(field.rel.to, components[1])
            return True
        except FieldDoesNotExist:
            return False

    def remove_invalid_fields(self, queryset, ordering, view, request):
        return [term for term in ordering
                if self.is_valid_field(queryset.model, term.lstrip('-'))]


class BaseApiViewSet(MethodAuthenticationMixin, viewsets.ModelViewSet, UpdatesMixin):
    """
    Include this as mixin to make your ListAPIView paginated & give it the ability to order by field name
    """
    pagination_class = StandardResultPagination

    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,
                       RelatedOrderingFilter,
                       SearchFilter,
                       )
    # renderers = settings.REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES']
    _serializer_class_for_fields = {}

    permission_classes = [DefaultPermission, ]

    def get_serializer_class_for_fields(self, serializer_class, fields):
        fields = fields.strip().split(',')
        fields.sort()
        fields = tuple(fields)
        if fields in self._serializer_class_for_fields:
            return self._serializer_class_for_fields[fields]

        # Doing this because a simple copy.copy() doesn't work here.
        meta = type('Meta', (serializer_class.Meta, object), {'fields': fields})
        limited_fields_serializer = type('LimitedFieldsSerializer', (serializer_class,),
                                         {'Meta': meta})
        self._serializer_class_for_fields[fields] = limited_fields_serializer
        return limited_fields_serializer

    def get_serializer_class(self):
        """
        Allow the `fields` query parameter to limit the returned fields
        in list and detail views.  `fields` takes a comma-separated list of
        fields.
        """
        serializer_class = super(BaseApiViewSet, self).get_serializer_class()
        fields = self.request.query_params.get('fields')
        if self.request.method == 'GET' and fields:
            return self.get_serializer_class_for_fields(serializer_class, fields)
        return serializer_class

    def _set_updated_by(self, request):
        token = get_jwt_token(request)
        return get_unverified_profile(token)

    def perform_create(self, serializer):
        updated_by = self._set_updated_by(self.request)
        serializer.save(updated_by=updated_by)

    def perform_update(self, serializer):
        updated_by = self._set_updated_by(self.request)
        serializer.save(updated_by=updated_by)

    def get_object(self):
        pk = check_uuid(self.kwargs.get(self.lookup_field))
        return super(BaseApiViewSet, self).get_object()


class BaseAttributeApiViewSet(BaseApiViewSet):
    permission_classes = [
        Or(UnauthenticatedReadOnlyPermission,
           AttributeAuthenticatedUserPermission)
    ]

    method_authentication_classes = {
        "GET": []
    }

    def perform_create(self, serializer):
        # Here is where we could set status based on user role
        # for now, make it always lowest when set by API, though this is also model default
        serializer.save(status=APPROVAL_STATUSES[-1][0])

    def perform_update(self, serializer):
        serializer.save(status=APPROVAL_STATUSES[-1][0])


class BaseProjectApiViewSet(BaseApiViewSet):
    project_lookup = None

    permission_classes = [
        Or(ProjectDataReadOnlyPermission,
           ProjectDataCollectorPermission,
           ProjectDataAdminPermission)
    ]

    def perform_update(self, serializer):
        requested_project = uuid.UUID(check_uuid(self.request.data.get('project')))
        existing_project = self.get_object().project.pk
        if requested_project != existing_project:
            raise ValidationError('Reassigning project data to another project not currently supported.')
        serializer.save()

    def limit_to_project(self, request, *args, **kwargs):
        model = self.get_queryset().model
        if hasattr(model, "project_lookup") and model.project_lookup is not None:
            project_filter = {model.project_lookup: check_uuid(kwargs["project_pk"])}
            self.queryset = self.get_queryset().filter(**project_filter)
        return self.queryset

    def list(self, request, *args, **kwargs):
        self.limit_to_project(request, *args, **kwargs)
        return super(BaseProjectApiViewSet, self).list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        self.limit_to_project(request, *args, **kwargs)
        return super(BaseProjectApiViewSet, self).retrieve(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        self.limit_to_project(request, *args, **kwargs)
        return super(BaseProjectApiViewSet, self).create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        self.limit_to_project(request, *args, **kwargs)
        return super(BaseProjectApiViewSet, self).update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        self.limit_to_project(request, *args, **kwargs)
        return super(BaseProjectApiViewSet, self).partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        self.limit_to_project(request, *args, **kwargs)
        return super(BaseProjectApiViewSet, self).destroy(request, *args, **kwargs)

    @list_route(methods=['POST'])
    def missing(self, request, *args, **kwargs):
        self.limit_to_project(request, *args, **kwargs)
        return super(BaseProjectApiViewSet, self).missing(
            request, *args, **kwargs
        )


class BaseChoiceApiViewSet(MethodAuthenticationMixin, viewsets.ViewSet):
    permission_classes = [UnauthenticatedReadOnlyPermission, ]

    method_authentication_classes = {
        "GET": []
    }


    # If we need to filter according to project role, we do this here
    def _filter(self, keys=None):
        choices = []
        model_choices = self.get_choices()
        for key, chc in model_choices.items():
            if keys is not None and key not in keys:
                continue
            choices.append({
                'name': key,
                'data': chc['data']
            })
        return choices

    @method_decorator(cache_page(60*60))
    def list(self, request):
        choices = self._filter()
        return Response(choices)

    def retrieve(self, request, pk=None):
        choices = self._filter(keys=[pk])
        try:
            return Response(choices[0])
        except IndexError:
            raise NotFound('{} choice not found.'.format(pk))

    def create(self, request):
        raise MethodNotAllowed('POST')

    def update(self, request, pk=None):
        raise MethodNotAllowed('PUT')

    def partial_update(self, request, pk=None):
        raise MethodNotAllowed('PATCH')

    def destroy(self, request, pk=None):
        raise MethodNotAllowed('DELETE')