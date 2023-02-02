from rest_framework import serializers

from users.exception import CreditAmountMustBePositive, CreditNotEnough
from users.models import Skill, Education, Experience, TeamUser, TransactionHistory
from users.serializers import UserSerializer


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = '__all__'


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = '__all__'


class ExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experience
        fields = '__all__'


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
