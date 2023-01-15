from django.urls import path

from foods.views import PaymentFoodLAV, PaymentFoodRUAV, PaymentFoodRUAVMe

app_name = 'foods'

urlpatterns = [
    path('payment-food/', PaymentFoodLAV.as_view(), name='payment-food-list'),
    path('payment-food/<uuid:pk>/', PaymentFoodRUAV.as_view(), name='payment-food-detail'),
    path('payment-food/me/', PaymentFoodRUAVMe.as_view(), name='payment-food-me'),
]
