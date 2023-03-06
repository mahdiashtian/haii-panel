from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from main.permissions import IsSuperUser, IsCeoOrManager, SafeMethodOnly
from teams.models import Team, MemberRecruitmentFilter, Activity, MembershipRequest
from teams.serializers import TeamSerializer, MemberRecruitmentFilterSerializer, ActivitySerializer, \
    MembershipRequestSerializer

User = get_user_model()


class ActivityViewSet(viewsets.ModelViewSet):
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer
    permission_classes = [IsSuperUser | IsCeoOrManager]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        return self.queryset.filter(team_id=self.kwargs['team_pk'], child=None)

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data['team'] = self.kwargs['team_pk']
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticated] + [SafeMethodOnly | (IsSuperUser | IsCeoOrManager)]
    pagination_class = PageNumberPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['is_confirmed']
    search_fields = ['name']

    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated & IsSuperUser])
    def confirm(self, request, pk=None):
        team = self.get_object()
        serializer = self.serializer_class(team, data={'is_confirmed': request.data.get('is_confirmed', None)},
                                           partial=True,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated & IsSuperUser])
    def users(self, request, pk=None):
        user = Profile.objects.filter(team_user_profile__team_id=self.kwargs['pk'])
        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(user, request)
        pf = ProfileSerializer
        pf.params = {"fields": ['id', 'first_name', 'last_name']}
        serializer = pf(user, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)

        return Response(serializer.data)

    def get_serializer_class(self):
        user = self.request.user
        if user.role() != "کاربر عادی":
            return super().get_serializer_class()
        serializer_class = self.serializer_class
        serializer_class.params = {"fields": ['id', 'name']}
        return serializer_class


class MemberRecruitmentFilterViewSet(viewsets.ModelViewSet):
    queryset = MemberRecruitmentFilter.objects.all()
    serializer_class = MemberRecruitmentFilterSerializer
    permission_classes = [IsSuperUser | IsCeoOrManager]

    def get_queryset(self):
        return self.queryset.filter(team_id=self.kwargs['team_pk'])

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data['team'] = self.kwargs['team_pk']
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class MembershipRequestViewSet(viewsets.ModelViewSet):
    queryset = MembershipRequest.objects.all()
    serializer_class = MembershipRequestSerializer

    def get_queryset(self):
        print(self.queryset)
        return self.queryset

    def get_permissions(self):
        if not self.action == 'create':
            self.permission_classes = [IsSuperUser | IsCeoOrManager]
        else:
            self.permission_classes = []
        return super().get_permissions()

    @action(detail=True, methods=['patch'], permission_classes=[IsCeoOrManager | IsSuperUser])
    def confirm(self, request, pk=None):
        member = self.get_object()
        serializer = self.serializer_class(member, data={'is_confirmed': request.data.get('is_confirmed', None)},
                                           partial=True,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
