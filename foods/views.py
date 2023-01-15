from rest_framework import generics

from foods.models import PaymentFood
from foods.serializer import PaymentFoodSerializer
from main.permissions import IsOwner, IsSuperUser


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
