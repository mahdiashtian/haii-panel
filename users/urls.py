from django.urls import re_path, path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenVerifyView

from users.views import TokenObtainPairView, TokenRefreshView, CheckDestinationAccountAV, SendCreditAV, \
    IncreaseCreditCardNumberVS, CreditCardNumberShowAP, TokenBlacklistView, SkillViewSet, ExperienceViewSet, \
    EducationViewSet,ProfileViewSet

app_name = 'users'

routers = DefaultRouter()
routers.register(r'increase-credit-card-number', IncreaseCreditCardNumberVS, basename='credit')
routers.register(r'skills', SkillViewSet, basename='skill')
routers.register(r'educations', EducationViewSet, basename='education')
routers.register(r'experiences', ExperienceViewSet, basename='experience')
routers.register(r'profiles', ProfileViewSet, basename='profile')

urlpatterns = [
    re_path(r"^auth/jwt/create/?", TokenObtainPairView.as_view(), name="jwt-create"),
    re_path(r"^auth/jwt/refresh/?", TokenRefreshView.as_view(), name="jwt-refresh"),
    re_path(r"^auth/jwt/verify/?", TokenVerifyView.as_view(), name="jwt-verify"),
    re_path(r"^auth/jwt/logout/?", TokenBlacklistView.as_view(), name="jwt-logout"),

    re_path(r"^check-destination-account/?", CheckDestinationAccountAV.as_view(), name="check-destination-account"),
    re_path(r"^send-credit/?", SendCreditAV.as_view(), name="send-credit"),

    path('credit-card-number-show/', CreditCardNumberShowAP.as_view(),
         name='credit-card-number-show'),

    path("", include(routers.urls)),

]
