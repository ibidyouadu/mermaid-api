from api.auth0_management import Auth0DatabaseAuthenticationAPI, Auth0Users
from .base import BaseAPISerializer
from rest_framework import permissions, viewsets
from rest_framework.exceptions import MethodNotAllowed, NotFound, ValidationError
from rest_framework.response import Response
from rest_framework.decorators import action

from ..models import Profile


class MeSerializer(BaseAPISerializer):
    class Meta:
        model = Profile
        fields = [
            'id',
            'first_name',
            'last_name',
            'full_name',
            'email',
            'created_on',
            'updated_on',
        ]


class AuthenticatedMePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated


class MeViewSet(viewsets.ModelViewSet):
    serializer_class = MeSerializer
    permission_classes = [AuthenticatedMePermission, ]

    def get_queryset(self):
        pass

    def list(self, request, *args, **kwargs):
        user = self.request.user
        profile = user.profile
        if profile is None:
            raise NotFound()

        return Response(self.serializer_class(profile).data)

    def put(self, request, *args, **kwargs):
        '''
        Used for updating a user's own profile details
        '''
        user = self.request.user
        profile = user.profile
        if profile is None:
            raise NotFound()

        me_serializer = MeSerializer(
            data=request.data, instance=profile)

        if me_serializer.is_valid() is False:
            errors = {'Profile': me_serializer.errors}
            raise ValidationError(errors)

        auth_user_ids = [au.user_id for au in profile.authusers.all()]
        auth_users_client = Auth0Users()
        email = me_serializer.validated_data.get('email')
        first_name = me_serializer.validated_data.get('first_name')
        last_name = me_serializer.validated_data.get('last_name')

        for user_id in auth_user_ids:
            auth_users_client.update({
                'user_id': user_id,
                'user_metadata': {
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email
                }
            })
        me_serializer.save()
        return Response(me_serializer.validated_data)

    def _get_email(self, profile):
        auth_user_ids = [au.user_id for au in profile.authusers.all()]
        auth_users_client = Auth0Users()
        for user_id in auth_user_ids:
            user_info = auth_users_client.get_user(user_id)
            for identity in user_info.get('identities') or []:
                provider = identity.get('connection')
                if provider != Auth0DatabaseAuthenticationAPI.CONNECTION:
                    continue
                return user_info.get('email')
        return None

    @action(detail=False, methods=['post'])
    def change_password(self, request, *args, **kwargs):
        user = self.request.user
        profile = user.profile
        if profile is None:
            raise NotFound()

        email = self._get_email(profile)
        if email is None:
            raise ValidationError('Unable to change password from 3rd party user accounts')

        auth = Auth0DatabaseAuthenticationAPI()
        return Response(auth.change_password(email))
