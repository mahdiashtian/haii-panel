from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, mixins, viewsets

from foods.models import PaymentFood, FoodAndDesire, WeeklyMeal, WeeklyMealUser
from foods.serializer import PaymentFoodSerializer, FoodAndDesireSerializer, WeeklyMealSerializer, \
    WeeklyMealUserSerializer
from main.permissions import IsOwner, IsSuperUser, IsSuperUserOrReadOnly


class FoodAndDesireViewSet(mixins.CreateModelMixin,
                           mixins.RetrieveModelMixin,
                           mixins.UpdateModelMixin,
                           mixins.ListModelMixin,
                           viewsets.GenericViewSet):
    queryset = FoodAndDesire.objects.all()
    serializer_class = FoodAndDesireSerializer
    permission_classes = [IsSuperUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['type']


class WeeklyMealViewSet(viewsets.ModelViewSet):
    serializer_class = WeeklyMealSerializer
    permission_classes = [IsSuperUserOrReadOnly]
    
    def get_queryset(self):
        date = timezone.now().date()
        queryset = WeeklyMeal.objects.filter(date__gte=date).order_by('date')
        return queryset


class WeeklyMealUserViewSet(viewsets.ModelViewSet):
    queryset = WeeklyMealUser.objects.all()
    serializer_class = WeeklyMealUserSerializer


class PaymentFoodRUAV(generics.RetrieveUpdateAPIView):
    permission_classes = (IsOwner,)
    queryset = PaymentFood.objects.all()
    serializer_class = PaymentFoodSerializer


class PaymentFoodRUAVMe(PaymentFoodRUAV):
    def get_object(self):
        return self.queryset.get(user=self.request.user.id)


class PaymentFoodLAV(generics.ListAPIView):
    permission_classes = (IsSuperUser,)
    queryset = PaymentFood.objects.all()
    serializer_class = PaymentFoodSerializer
