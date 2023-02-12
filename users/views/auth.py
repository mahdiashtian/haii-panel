import random

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework import status
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt import views as jwt_views
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from main.melipayamak import Api
from users.exception import CodeInvalid, SerializersException
from users.jwt_auth import set_jwt_cookies, set_jwt_access_cookie, unset_jwt_cookies
from users.serializers.auth import PhoneVerifySerializer, PhoneSubmitSerializer

CACHE_TTL = settings.CACHE_TTL
CACHE_TTL_CODE = settings.CACHE_TTL_CODE
username = settings.SMS_USERNAME
password = settings.SMS_PASSWORD
from_ = settings.SMS_FROM
api = Api(username, password)
sms = api.sms()

User = get_user_model()


class TokenObtainPairView(jwt_views.TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])
        response = Response(serializer.validated_data, status=status.HTTP_200_OK)
        access_token = response.data['access']
        refresh_token = response.data['refresh']
        set_jwt_cookies(response, access_token, refresh_token)
        return response


class TokenRefreshView(jwt_views.TokenRefreshView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        access_token = response.data['access']
        set_jwt_access_cookie(response, access_token)
        return response


class TokenBlacklistView(APIView):
    def post(self, request, *args, **kwargs):
        response = Response(data={'detail': 'Successfully logged out.'}, status=status.HTTP_200_OK)
        unset_jwt_cookies(response)
        return response


class PhoneVerifyView(APIView):
    throttle_classes = [UserRateThrottle]

    def initial(self, request, *args, **kwargs):
        """
        Runs anything that needs to occur prior to calling the method handler.
        """
        self.format_kwarg = self.get_format_suffix(**kwargs)

        # Perform content negotiation and store the accepted info on the request
        neg = self.perform_content_negotiation(request)
        request.accepted_renderer, request.accepted_media_type = neg

        # Determine the API version, if versioning is in use.
        version, scheme = self.determine_version(request, *args, **kwargs)
        request.version, request.versioning_scheme = version, scheme

        # Ensure that the incoming request is permitted
        self.perform_authentication(request)
        self.check_permissions(request)

    def post(self, request, *args, **kwargs):
        serializer = PhoneVerifySerializer(data=request.data)

        if serializer.is_valid():
            self.check_throttles(request)
            # code = random.randint(10000, 99999)
            code = 11111
            phone = serializer.validated_data['phone']
            # result = sms.send(phone, from_, code)
            user = request.user
            user_agents = request.user_agent
            browser = user_agents.browser
            os = user_agents.os
            information = {
                'browser': {
                    'family': browser.family,
                    'version': browser.version_string,
                },
                'os': {
                    'family': os.family,
                    'version': os.version_string,
                },
                'code': str(code),
                'phone': phone,
                'verified': False,
            }
            cache.set(f"phone-{str(user.id)}", information, timeout=CACHE_TTL)
            return Response({'detail': 'کد تایید برای شما با موفقیت ارسال شد'}, status=status.HTTP_200_OK)
        raise SerializersException


class PhoneSubmitView(APIView):
    def check_device(self, information, validated_data):
        user_agent = self.request.user_agent
        browser = user_agent.browser
        os = user_agent.os
        family_browser = browser.family
        version_browser = browser.version_string
        family_os = os.family
        version_os = os.version_string
        code = validated_data['code']

        if information['code'] == code and information['browser']['family'] == family_browser and \
                information['browser']['version'] == version_browser and information['os']['family'] == family_os and \
                information['os']['version'] == version_os:
            return True
        return False

    def post(self, request, *args, **kwargs):
        user = request.user
        serializer = PhoneSubmitSerializer(data=request.data)
        if serializer.is_valid():
            information = cache.get(f"phone-{str(user.id)}")
            validated_data = serializer.validated_data
            if information is None:
                raise CodeInvalid
            if information['verified']:
                return Response({'detail': 'شما قبلا تایید شده اید'}, status=status.HTTP_400_BAD_REQUEST)
            elif self.check_device(information, validated_data):
                information['verified'] = True
                cache.set(f"phone-{str(user.id)}", information, timeout=CACHE_TTL_CODE)
                return Response({'detail': 'شماره تلفن شما با موفقیت تایید شد'}, status=status.HTTP_200_OK)
            raise CodeInvalid
        raise SerializersException
