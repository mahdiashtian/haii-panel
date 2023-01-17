from rest_framework import generics, mixins
from rest_framework.viewsets import GenericViewSet

from foods.models import PaymentFood, FoodAndDesire
from foods.serializer import PaymentFoodSerializer, FoodAndDesireSerializer
from main.permissions import IsOwner, IsSuperUser


class FoodAndDesireViewSet(mixins.CreateModelMixin,
                           mixins.RetrieveModelMixin,
                           mixins.UpdateModelMixin,
                           mixins.ListModelMixin,
                           GenericViewSet):
    queryset = FoodAndDesire.objects.all()
    serializer_class = FoodAndDesireSerializer
    permission_classes = [IsSuperUser]


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
