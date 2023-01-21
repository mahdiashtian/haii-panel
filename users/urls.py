from django.urls import re_path
from rest_framework_simplejwt.views import TokenVerifyView
from user.views import TokenObtainPairView, TokenRefreshView

app_name = 'users'

urlpatterns = [
    re_path(r"^auth/jwt/create/?", TokenObtainPairView.as_view(), name="jwt-create"),
    re_path(r"^auth/jwt/refresh/?", TokenRefreshView.as_view(), name="jwt-refresh"),
    re_path(r"^auth/jwt/verify/?", TokenVerifyView.as_view(), name="jwt-verify"),

]
