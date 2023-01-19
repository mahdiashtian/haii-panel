from django.utils import timezone
from rest_framework import serializers

from foods.exception import DateIsPast
from foods.models import WeeklyMeal, FoodAndDesire, PaymentFood, WeeklyMealUser


class WeeklyMealSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        result = super().to_representation(instance)
        if instance.food:
            result['food'] = FoodAndDesireSerializer(instance.food).data
        if instance.desire:
            result['desire'] = FoodAndDesireSerializer(instance.desire).data
        return result

    def validate_date(self, value):
        today = timezone.now().date()
        if value < today:
            raise DateIsPast
        return value

    class Meta:
        model = WeeklyMeal
        fields = '__all__'
        read_only_fields = ('price',)


class WeeklyMealUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeeklyMealUser
        fields = '__all__'


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
    weekly_meal_payment = WeeklyMealUserSerializer(many=True, read_only=True)

    class Meta:
        model = PaymentFood
        fields = '__all__'
        read_only_fields = ('user',)
