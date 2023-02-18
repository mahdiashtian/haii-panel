from django.conf import settings
from django.db.models import Sum
from django.utils import timezone
from rest_framework import serializers

from foods.exception import DateIsPast, LimitFoodAndDesire, LimitMeal
from foods.models import WeeklyMeal, FoodAndDesire, PaymentFood, WeeklyMealUser


class WeeklyMealSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        result = super().to_representation(instance)
        if instance.food:
            result['food'] = FoodAndDesireSerializer(instance.food).data
        if instance.desire:
            result['desire'] = FoodAndDesireSerializer(instance.desire, many=True).data
        return result

    def validate_date(self, value):
        today = timezone.now().date()
        date_reservation = today + timezone.timedelta(days=settings.ADMIN_DAY_RESERVATION)
        if value < date_reservation:
            raise DateIsPast
        return value

    def save(self, **kwargs):
        result = super(WeeklyMealSerializer, self).save()
        if result.food:
            result.price += result.food.price
        if result.desire:
            result.price += result.desire.all().aggregate(Sum('price'))['price__sum']
        result.save()
        return result

    class Meta:
        model = WeeklyMeal
        fields = '__all__'
        read_only_fields = ('price',)


class WeeklyMealUserSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        result = super().to_representation(instance)
        if instance.weekly_meal_food:
            result['weekly_meal_food'] = WeeklyMealSerializer(instance.weekly_meal_food).data
        return result

    def validate(self, attrs):
        count = attrs['count']
        weekly_meal = attrs['weekly_meal_food']
        user = self.context['request'].user
        meal = weekly_meal.meal
        date = weekly_meal.date
        if user.is_superuser:
            return attrs
        if count > weekly_meal.food.limit:
            raise LimitFoodAndDesire
        if user.payment_food_user.weekly_meal_user_payment.filter(weekly_meal_food__date=date,
                                                                  weekly_meal_food__meal=meal).exists():
            raise LimitMeal
        return attrs

    class Meta:
        model = WeeklyMealUser
        exclude = ('payment',)


class FoodAndDesireSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodAndDesire
        fields = '__all__'


class PaymentFoodSerializer(serializers.ModelSerializer):
    def get_bills(self, obj):
        debt = obj.user.credit
        return {
            "debt": abs(debt) if debt < 0 else 0,
            "credit": debt if debt > 0 else 0,
        }

    bills = serializers.SerializerMethodField()
    weekly_meal_user_payment = WeeklyMealUserSerializer(many=True, read_only=True)

    class Meta:
        model = PaymentFood
        fields = '__all__'
        read_only_fields = ('user',)
