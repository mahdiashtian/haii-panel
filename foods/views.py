import uuid

from django.db.models import Sum
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, mixins, viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response

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

    @action(detail=False, methods=['post'])
    def bulk_create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class WeeklyMealUserViewSet(viewsets.ModelViewSet):
    queryset = WeeklyMealUser.objects.all()
    serializer_class = WeeklyMealUserSerializer

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response.data.append({'credit': request.user.credit})
        return response

    def get_queryset(self):
        return self.queryset.filter(payment__user=self.request.user)

    def perform_create(self, serializer):
        payment = PaymentFood.objects.get_or_create(user=self.request.user)
        validated_data = serializer.validated_data
        if type(validated_data) == list:
            price = 0
            for data in validated_data:
                price += data['weekly_meal_food'].price * data['count']
        else:
            price = validated_data['weekly_meal_food'].price * validated_data['count']
        user = self.request.user
        if user.credit < price:
            raise serializers.ValidationError('Not enough money')
        print(user.credit)
        user.credit -= price
        print(price)
        user.save()
        print(user.credit)
        serializer.save(payment=payment[0])

    @action(detail=False, methods=['post'])
    def bulk_create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=True)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors[2], status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def bulk_delete(self, request, *args, **kwargs):
        user = self.request.user
        data = request.data
        if not isinstance(data, list):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        id_list = [uuid.UUID(item.get('id')) if item.get('id') else None for item in data]

        queryset = self.get_queryset().filter(id__in=id_list)
        if not queryset:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        credit = queryset.aggregate(Sum('weekly_meal_food__price'))
        user.credit += credit['weekly_meal_food__price__sum']
        user.save()
        queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


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
