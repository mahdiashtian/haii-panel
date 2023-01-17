from django.urls import path, include
from rest_framework.routers import DefaultRouter

from foods.views import PaymentFoodLAV, PaymentFoodRUAV, PaymentFoodRUAVMe, FoodAndDesireViewSet

app_name = 'foods'

router = DefaultRouter()
router.register('food-and-desire', FoodAndDesireViewSet, basename='food-and-desire')

urlpatterns = [
    path('payment-food/', PaymentFoodLAV.as_view(), name='payment-food-list'),
    path('payment-food/<uuid:pk>/', PaymentFoodRUAV.as_view(), name='payment-food-detail'),
    path('payment-food/me/', PaymentFoodRUAVMe.as_view(), name='payment-food-me'),

    path('', include(router.urls)),
]
