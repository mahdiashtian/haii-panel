from django.conf import settings
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.filters import SearchFilter
from rest_framework.generics import UpdateAPIView, ListCreateAPIView
from rest_framework.response import Response

from main.melipayamak import Api
from main.permissions import IsSuperUser, IsCurrentUser
from users.exception import PasswordInvalid
from users.models import Profile
from users.serializers import ProfileSerializer, ConfirmProfileSerializer, ChangePasswordSerializer

username = settings.SMS_USERNAME
password = settings.SMS_PASSWORD
from_ = settings.SMS_FROM
api = Api(username, password)
sms = api.sms()


class ProfileList(generics.ListAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsSuperUser]

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ProfileRetrieveUpdate(generics.RetrieveUpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsCurrentUser | IsSuperUser]


class ProfileRetrieveUpdateMe(ProfileRetrieveUpdate):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsCurrentUser | IsSuperUser]

    def get_object(self):
        return self.queryset.get(user__id=self.request.user.id)


class ConfirmProfileAPIView(ListCreateAPIView):
    queryset = Profile.objects.all()
    permission_classes = [IsSuperUser]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['gender', 'marital_status', 'is_confirmed']
    search_fields = ['user__first_name', 'user__last_name', 'phone_number']

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ProfileSerializer
        return ConfirmProfileSerializer

    def create(self, request, format=None):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            profile_ids = serializer.validated_data['profile_ids']
            condition = serializer.validated_data['condition']
            reason = serializer.validated_data.get('reason', None)

            profiles = Profile.objects.filter(id__in=profile_ids)
            profiles.update(is_confirmed=condition)
            if reason:
                phone_numbers = profiles.values_list('phone_number', flat=True)
                for i in phone_numbers:
                    sms.send(i, from_, reason)
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsCurrentUser]

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            if not self.object.check_password(serializer.data.get("old_password")):
                raise PasswordInvalid
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'پسورد با موفقیت تغییر یافت.',
                'data': []
            }

            return Response(response)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
