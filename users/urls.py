from django.urls import re_path, path, include
from rest_framework import routers
from rest_framework_simplejwt.views import TokenVerifyView

from users.views import TokenObtainPairView, TokenRefreshView, CheckDestinationAccount, SendCredit, \
    IncreaseCreditCardNumberViewSet

app_name = 'users'

routers = routers.DefaultRouter()
routers.register(r'increase-credit-card-number', IncreaseCreditCardNumberViewSet, basename='credit')

urlpatterns = [
    re_path(r"^auth/jwt/create/?", TokenObtainPairView.as_view(), name="jwt-create"),
    re_path(r"^auth/jwt/refresh/?", TokenRefreshView.as_view(), name="jwt-refresh"),
    re_path(r"^auth/jwt/verify/?", TokenVerifyView.as_view(), name="jwt-verify"),

    re_path(r"^check-destination-account/?", CheckDestinationAccount.as_view(), name="check-destination-account"),
    re_path(r"^send-credit/?", SendCredit.as_view(), name="send-credit"),

    path("", include(routers.urls)),

]
