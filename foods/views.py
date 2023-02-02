import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, viewsets, status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from foods.exception import DateIsPast, NotEnoughMoney, InputNotValid
from foods.models import PaymentFood, FoodAndDesire, WeeklyMeal, WeeklyMealUser
from foods.serializer import PaymentFoodSerializer, FoodAndDesireSerializer, WeeklyMealSerializer, \
    WeeklyMealUserSerializer
from main.permissions import IsOwner, IsSuperUser, IsSuperUserOrReadOnly

User = get_user_model()


class FoodAndDesireViewSet(viewsets.ModelViewSet):
    queryset = FoodAndDesire.objects.all().order_by('name')
    serializer_class = FoodAndDesireSerializer
    permission_classes = [IsSuperUser]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['type']
    search_fields = ['name']
    pagination_class = PageNumberPagination


class WeeklyMealViewSet(viewsets.ModelViewSet):
    serializer_class = WeeklyMealSerializer
    queryset = WeeklyMeal.objects.all()
    permission_classes = [IsSuperUserOrReadOnly]
    filter_backends = [DjangoFilterBackend]

    filterset_fields = {
        'date': ['lt', 'gt'],
    }

    @action(detail=False, methods=['get'], permission_classes=[IsSuperUser])
    def today(self, request, *args, **kwargs):
        queryset = self.queryset.filter(date=timezone.now().date())
        paginator = PageNumberPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = self.get_serializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    @action(detail=False, methods=['post'])
    def bulk_create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors[0], status=status.HTTP_400_BAD_REQUEST)

    def perform_destroy(self, instance):
        if not instance.is_deletable():
            raise DateIsPast
        instance.delete()


class WeeklyMealUserViewSet(viewsets.ModelViewSet):
    queryset = WeeklyMealUser.objects.all()
    serializer_class = WeeklyMealUserSerializer
    filter_backends = [DjangoFilterBackend]

    filterset_fields = {
        'weekly_meal_food__date': ['lt', 'gt'],
    }

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response.data.append({'credit': request.user.credit})
        return response

    def get_queryset(self):
        return self.queryset.filter(payment__user=self.request.user)

    def perform_create(self, serializer):
        payment = PaymentFood.objects.get_or_create(user=self.request.user)
        # create logic payment
        validated_data = serializer.validated_data
        if type(validated_data) == list:
            price = 0
            for data in validated_data:
                price += data['weekly_meal_food'].price * data['count']
        else:
            price = validated_data['weekly_meal_food'].price * validated_data['count']
        user = self.request.user
        if user.credit < price:
            raise NotEnoughMoney
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
        data = request.data
        if not isinstance(data, list):
            raise InputNotValid
        id_list = [uuid.UUID(item.get('id')) if item.get('id') else None for item in data]

        today = timezone.now().date()
        date = today + timezone.timedelta(days=settings.USER_DAY_RESERVATION)
        queryset = self.get_queryset().filter(id__in=id_list, weekly_meal_food__date__gte=date)
        if not queryset:
            raise DateIsPast

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
