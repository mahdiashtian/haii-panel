from django.contrib.auth import get_user_model
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from main.permissions import IsSuperUser, IsCurrentUser, UserHasProfile
from users.models import Skill, Education, Experience
from users.serializers import SkillSerializer, EducationSerializer, ExperienceSerializer

User = get_user_model()


class BaseViewSet(viewsets.GenericViewSet,
                  mixins.CreateModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin):
    lookup_field = 'pk'
    lookup_url_kwarg = 'pk'
    permission_classes = [IsAuthenticated & UserHasProfile & (IsSuperUser | IsCurrentUser)]

    def perform_update(self, serializer):
        serializer.save(profile=self.request.user.profile_user)

    def perform_create(self, serializer):
        serializer.save(profile=self.request.user.profile_user)


class SkillViewSet(BaseViewSet):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer


class EducationViewSet(BaseViewSet):
    queryset = Education.objects.all()
    serializer_class = EducationSerializer


class ExperienceViewSet(BaseViewSet):
    queryset = Experience.objects.all()
    serializer_class = ExperienceSerializer
