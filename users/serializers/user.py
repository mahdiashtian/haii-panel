from django.contrib.auth import get_user_model
from rest_framework import serializers

from users.exception import UserDoesNotExist, CreditAmountMustBePositive, CreditNotEnough, SelfCredit
from users.models import TransactionHistory

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ['password', 'groups', 'user_permissions', 'date_joined', 'last_login']


class CheckDestinationAccountSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)

    def validate_username(self, value):
        user = User.objects.filter(username=value).exists()
        if not user:
            raise UserDoesNotExist
        return value


class SendCreditSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    amount = serializers.IntegerField()

    def validate_username(self, value):
        user = User.objects.filter(username=value).exists()
        if not user:
            raise UserDoesNotExist
        if self.context['request'].user.username == value:
            raise SelfCredit
        return value

    def validate_amount(self, value):
        user = self.context['request'].user
        if value < 0:
            raise CreditAmountMustBePositive
        if user.credit < value:
            raise CreditNotEnough
        return value


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
