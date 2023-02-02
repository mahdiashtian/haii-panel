import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class ID(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class PaymentFood(ID):
    # weekly_meal_user_payment :Inversely related to 'PaymentFood' from 'WeeklyMealUser'
    class PaymentChoices(models.TextChoices):
        DFC = 'DFC', ('کسر از اعتبار')
        PG = 'PG', ('درگاه پراخت')
        ETQ = 'ETQ', ('هربار سوال شود')

    default_payment = models.CharField(max_length=3, choices=PaymentChoices.choices, default=PaymentChoices.DFC)
    user = models.OneToOneField('users.User', on_delete=models.CASCADE, related_name='payment_food_user')

    def __str__(self):
        return f'PaymentFood: {self.user}'

    class Meta:
        app_label = 'foods'


class FoodAndDesire(ID):
    # weekly_meal_desire :Inversely related to 'FoodAndDesire' from 'WeeklyMeal'
    # weekly_meal_food :Inversely related to 'FoodAndDesire' from 'WeeklyMeal'

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


class WeeklyMealUser(ID):
    class PaymentChoices(models.TextChoices):
        DFC = 'DFC', ('کسر از اعتبار')
        PG = 'PG', ('درگاه پراخت')

    type_payment = models.CharField(max_length=3, choices=PaymentChoices.choices, default=PaymentChoices.DFC)
    count = models.PositiveIntegerField(verbose_name='تعداد', default=1)
    payment = models.ForeignKey('foods.PaymentFood', on_delete=models.CASCADE, related_name='weekly_meal_user_payment',
                                verbose_name='پرداخت')
    weekly_meal_food = models.ForeignKey('foods.WeeklyMeal', on_delete=models.CASCADE,
                                         related_name='weekly_meal_user_weekly_meal_food', verbose_name="غذای انتخابی")

    def save(
            self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        if self.payment.default_payment != "ETQ":
            self.type_payment = self.payment.default_payment
        super().save(force_insert, force_update, using, update_fields)

    class Meta:
        app_label = 'foods'
        unique_together = ('payment', 'weekly_meal_food')


class WeeklyMeal(ID):
    # weekly_meal_user_weekly_meal_food :Inversely related to 'WeeklyMeal' from 'WeeklyMealUser'

    class ChoiceMeal(models.TextChoices):
        BREAKFAST = 'BREAKFAST', ('صبحانه')
        LUNCH = 'LUNCH', ('ناهار')
        DINNER = 'DINNER', ('شام')

    date = models.DateField(verbose_name='تاریخ')
    food = models.ForeignKey('foods.FoodAndDesire', on_delete=models.CASCADE, verbose_name='غذا',
                             related_name='weekly_meal_food', limit_choices_to={'type': 'FOOD'}, null=True, blank=True)
    desire = models.ForeignKey('foods.FoodAndDesire', on_delete=models.CASCADE, verbose_name='پیش غذا',
                               related_name='weekly_meal_desire', limit_choices_to={'type': 'DESIRE'}, null=True,
                               blank=True)
    meal = models.CharField(max_length=9, choices=ChoiceMeal.choices, verbose_name='نوع وعده')
    price = models.PositiveBigIntegerField(verbose_name='قیمت', default=0)

    def save(
            self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        if self.food:
            self.price += self.food.price
        if self.desire:
            self.price += self.desire.price

        super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return f'{self.food}:{self.desire} - {self.date} - {self.meal}'

    def is_deletable(self):
        return self.date > timezone.now().date() + timezone.timedelta(days=settings.ADMIN_DAY_RESERVATION)

    class Meta:
        app_label = 'foods'
        unique_together = (('food', 'date', 'meal'), ('desire', 'date', 'meal'))
