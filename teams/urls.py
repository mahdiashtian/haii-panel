from django.urls import path, include
from rest_framework_nested import routers

from teams.views import TeamViewSet, ActivityViewSet, MemberRecruitmentFilterViewSet, MembershipRequestViewSet

app_name = 'teams'

nested_router = routers.SimpleRouter()
nested_router.register('teams', TeamViewSet, basename='teams')
nested_router.register('member-request', MembershipRequestViewSet, basename='member-request')
activity_router = routers.NestedSimpleRouter(nested_router, 'teams', lookup='team')
activity_router.register('activities', ActivityViewSet, basename='activities')
activity_router.register('team-filters', MemberRecruitmentFilterViewSet, basename='filter')

urlpatterns = [

    path('', include(nested_router.urls)),
    path('', include(activity_router.urls)),
]
