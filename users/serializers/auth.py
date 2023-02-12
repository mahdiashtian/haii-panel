from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class PhoneVerifySerializer(serializers.Serializer):
    default_error_messages = {
        'invalid': 'شماره تلفن صحیح نیست',
    }

    phone = serializers.RegexField(regex='^(0)9(0[1-5]|[1 3]\d|2[0-2]|98)\d{7}$', max_length=13, required=True,
                                   error_messages=default_error_messages)


class PhoneSubmitSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=6, required=True)
