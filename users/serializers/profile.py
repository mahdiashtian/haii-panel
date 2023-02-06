from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers

from users.models import Profile, Foreigner, Iranian, Child
from users.serializers import SkillSerializer, EducationSerializer, ExperienceSerializer


class IranianSerializer(serializers.ModelSerializer):
    class Meta:
        model = Iranian
        fields = '__all__'


class ForeignerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Foreigner
        fields = '__all__'


class ChildSerializer(serializers.ModelSerializer):
    class Meta:
        model = Child
        fields = '__all__'


class ProfileSerializer(WritableNestedModelSerializer):
    child = ChildSerializer(many=True)
    iranian = IranianSerializer()
    foreigner = ForeignerSerializer()
    skill = SkillSerializer(many=True, read_only=True)
    education = EducationSerializer(many=True, read_only=True)
    experience = ExperienceSerializer(many=True, read_only=True)


    class Meta:
        model = Profile
        fields = '__all__'
