import uuid

from django.db import models


class ID(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class PaymentFood(ID):
    # weekly_meal_payment :Inversely related to 'PaymentFood' from 'WeeklyMeal'

    class PaymentChoices(models.TextChoices):
        DFC = 'DFC', ('کسر از اعتبار')
        PG = 'PG', ('درگاه پراخت')
        ETQ = 'ETQ', ('هربار سوال شود')

    default_payment = models.CharField(max_length=3, choices=PaymentChoices.choices, default=PaymentChoices.DFC)
    user = models.OneToOneField('users.User', on_delete=models.CASCADE, related_name='payment_food')

    class Meta:
        app_label = 'foods'


class FoodAndDesire(ID):
    # weekly_meal_food :Inversely related to 'FoodAndDesire' from 'WeeklyMeal'
    # weekly_meal_desire :Inversely related to 'FoodAndDesire' from 'WeeklyMeal'

    class ChoiceFoodOrDesire(models.TextChoices):
        FOOD = 'FOOD', ('غذا')
        DESIRE = 'DESIRE', ('پیش غذا')

    name = models.CharField(max_length=100, verbose_name='نام')
    description = models.TextField(verbose_name='توضیحات')
    price = models.PositiveBigIntegerField(verbose_name='قیمت')
    limit = models.PositiveIntegerField(verbose_name='محدودیت')
    type = models.CharField(max_length=6, choices=ChoiceFoodOrDesire.choices, verbose_name='غذا/پیش غذا')

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'foods'


class WeeklyMeal(ID):
    class ChoiceMeal(models.TextChoices):
        BREAKFAST = 'BREAKFAST', ('صبحانه')
        LUNCH = 'LUNCH', ('ناهار')
        DINNER = 'DINNER', ('شام')

    date = models.DateField(verbose_name='تاریخ')
    food = models.ForeignKey('foods.FoodAndDesire', on_delete=models.CASCADE, verbose_name='غذا',
                             related_name='weekly_meal_food')
    desire = models.ForeignKey('foods.FoodAndDesire', on_delete=models.CASCADE, verbose_name='پیش غذا',
                               related_name='weekly_meal_desire')
    meal = models.CharField(max_length=9, choices=ChoiceMeal.choices, verbose_name='نوع وعده')
    payment = models.ForeignKey('foods.PaymentFood', on_delete=models.CASCADE, verbose_name='پرداخت',
                                related_name='weekly_meal_payment')

    class Meta:
        app_label = 'foods'
