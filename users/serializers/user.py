from django.contrib.auth import get_user_model
from rest_framework import serializers

from users.exception import UserDoesNotExist, CreditAmountMustBePositive, CreditNotEnough, SelfCredit

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(required=False)

    class Meta:
        model = User
        exclude = ['password', 'groups', 'user_permissions', 'date_joined', 'last_login']


class CheckDestinationAccountSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)

    def validate_username(self, value):
        user = User.objects.filter(username=value).exists()
        if not user:
            raise UserDoesNotExist
        if user == self.context['request'].user:
            raise SelfCredit
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
        if value <= 0:
            raise CreditAmountMustBePositive
        if user.credit < value:
            raise CreditNotEnough
        return value

# class UserListSerializer(serializers.ModelSerializer):
#     profile_user = serializers.SerializerMethodField()
#     payment_food_user = serializers.SerializerMethodField()
#     url_profile = serializers.HyperlinkedIdentityField(view_name='profile-detail', lookup_field='profile__id')
#
#     def get_profile_user(self, obj):
#         serializer_class = ProfileSerializer
#         return serializer_class(obj.profile).data
#
#     def get_payment_food_user(self, obj):
#         serializer_class = PaymentFoodSerializer
#         serializer_class.Meta.fields = ['bills']
#         return serializer_class(obj.profile).data
#
#     class Meta:
#         model = User
#         fields = "__all__"
