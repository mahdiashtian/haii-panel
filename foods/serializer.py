from rest_framework import serializers

from foods.models import WeeklyMeal


class WeeklyMealSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeeklyMeal
        fields = '__all__'
