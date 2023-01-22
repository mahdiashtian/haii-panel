from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt import views as jwt_views
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from users.jwt_auth import set_jwt_cookies, set_jwt_access_cookie

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
