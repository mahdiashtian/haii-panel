from rest_framework import serializers

from foods.models import WeeklyMeal, FoodAndDesire, PaymentFood


class WeeklyMealSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeeklyMeal
        fields = '__all__'


class FoodAndDesireSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodAndDesire
        fields = '__all__'


class PaymentFoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentFood
        fields = '__all__'
