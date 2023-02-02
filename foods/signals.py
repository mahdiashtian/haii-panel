from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver

from foods.models import WeeklyMeal, WeeklyMealUser


@receiver(pre_delete, sender=WeeklyMeal)
def credit_user_pre_delete_weekly_meal(sender, instance, **kwargs):
    price = instance.price
    for i in instance.weekly_meal_user_weekly_meal_food.all():
        user = i.payment.user
        user.credit += price * i.count
        user.save()


@receiver(pre_delete, sender=WeeklyMealUser)
def credit_user_pre_delete_weekly_meal_user(sender, instance, **kwargs):
    price = instance.weekly_meal_food.price
    user = instance.payment.user
    user.credit += price * instance.count
    user.save()


@receiver(pre_save, sender=WeeklyMealUser)
def credit_user_pre_save_weekly_meal_user(sender, instance, **kwargs):
    price = instance.weekly_meal_food.price
    user = instance.payment.user
    user.credit -= price * instance.count
    user.save()
