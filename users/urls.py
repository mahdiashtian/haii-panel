from django.urls import re_path
from rest_framework_simplejwt.views import TokenVerifyView

from users.views import TokenObtainPairView, TokenRefreshView, CheckDestinationAccount, SendCredit

app_name = 'users'

urlpatterns = [
    re_path(r"^auth/jwt/create/?", TokenObtainPairView.as_view(), name="jwt-create"),
    re_path(r"^auth/jwt/refresh/?", TokenRefreshView.as_view(), name="jwt-refresh"),
    re_path(r"^auth/jwt/verify/?", TokenVerifyView.as_view(), name="jwt-verify"),
    re_path(r"^check-destination-account/?", CheckDestinationAccount.as_view(), name="check-destination-account"),
    re_path(r"^send-credit/?", SendCredit.as_view(), name="send-credit"),

]
