from rest_framework import serializers

from users.exception import CreditAmountMustBePositive, CreditNotEnough, MaximumSkill
from users.models import Skill, Education, Experience, TeamUser, TransactionHistory
from users.serializers import UserSerializer


class SkillSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        user = self.context["request"].user
        skills = user.profile_user.skill_profile.count()
        method = self.context['request'].method
        if method == 'POST' and skills >= 3:
            raise MaximumSkill
        return attrs

    class Meta:
        model = Skill
        exclude = ('profile',)
        read_only_fields = ('id',)


class ExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experience
        exclude = ('profile',)
        read_only_fields = ('id',)


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        exclude = ('profile',)
        read_only_fields = ('id',)


class TeamUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamUser
        fields = '__all__'


class TransactionHistorySerializer(serializers.ModelSerializer):
    user_receiver = UserSerializer(read_only=True)
    user_sender = UserSerializer(read_only=True)

    def validate_price(self, value):
        user = self.context['request'].user
        if value < 0:
            raise CreditAmountMustBePositive
        if user.credit < value:
            raise CreditNotEnough
        return value

    class Meta:
        model = TransactionHistory
        fields = "__all__"
        read_only_fields = ('user_sender', 'status', 'date', 'user_receiver')
