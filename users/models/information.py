import uuid

from django.db import models

from utils.utils import upload_image_path


class ID(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class BaseInformationModel(models.Model):
    name = models.CharField(max_length=255, verbose_name='نام')
    description = models.TextField(verbose_name='توضیحات')
    profile = models.ForeignKey('users.Profile', on_delete=models.CASCADE, related_name='%(class)s_profile',
                                verbose_name='پروفایل')

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class Education(ID, BaseInformationModel):
    class GradeChoices(models.TextChoices):
        CYCLE = 'CY', ('سیکل')
        DIPLOM = 'DI', ('دیپلم')
        KARSHENASI = 'MA', ('کارشناسی')
        KARSHENASI_ARSHAD = 'MP', ('کارشناسی ارشد')
        DOCTORA = 'DA', ('دکترا')

    major = models.CharField(max_length=255, verbose_name='رشته تحصیلی')
    grade = models.CharField(max_length=23, choices=GradeChoices.choices, verbose_name='مقطع تحصیلی')
    gpa = models.FloatField(verbose_name='معدل')
    image = models.ImageField(upload_to=upload_image_path, verbose_name='تصویر لوگو موسسه')
    start = models.DateField(verbose_name='تاریخ شروع')
    stop = models.DateField(verbose_name='تاریخ پایان')
    is_student = models.BooleanField(verbose_name='تحصیل/عدم تحصیل')

    class Meta:
        app_label = 'users'


class Skill(ID, BaseInformationModel):
    class Meta:
        app_label = 'users'


class Experience(ID, BaseInformationModel):
    image = models.ImageField(upload_to=upload_image_path, verbose_name='تصویر لوگو موسسه')
    company = models.CharField(max_length=255, verbose_name='نام شرکت')
    start = models.DateField(verbose_name='تاریخ شروع')
    stop = models.DateField(verbose_name='تاریخ پایان')

    class Meta:
        app_label = 'users'


class TeamUser(models.Model):
    class MembershipChoices(models.TextChoices):
        PERMANENT = 'PE', ('دائمی')
        FREELANCER = 'FR', ('فریلنسر')
        LEARNER = 'LE', ('کارآموز')

    class Condition(models.TextChoices):
        confirmed = 'C', ('تایید شده')
        pending = 'P', ('در انتظار تایید')
        rejected = 'R', ('رد شده')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    team = models.ForeignKey('teams.Team', on_delete=models.CASCADE, related_name='team_user_team', verbose_name='تیم')
    profile = models.OneToOneField('users.Profile', on_delete=models.CASCADE, related_name='team_user_profile',
                                   verbose_name='پروفایل')
    membership_type = models.CharField(max_length=2, choices=MembershipChoices.choices, verbose_name='نوع عضویت')

    class Meta:
        app_label = 'users'


class TransactionHistory(models.Model):
    class PaymentChoices(models.TextChoices):
        CBC = 'CBC', ('کارت به کارت')
        PG = 'PG', ('درگاه پراخت')
        TT = 'TT', ('انتقال')

    class StatusChoices(models.TextChoices):
        REJECTED = 'RE', ('رد شده')
        ACCEPTED = 'AC', ('تایید شده')
        WAITING = 'WA', ('در انتظار تایید')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction_type = models.CharField(max_length=3, choices=PaymentChoices.choices, verbose_name='نوع تراکنش')
    price = models.IntegerField(verbose_name='مبلغ')
    date = models.DateField(auto_now_add=True, verbose_name='تاریخ')
    status = models.CharField(max_length=2, choices=StatusChoices.choices, verbose_name='وضعیت',
                              default=StatusChoices.WAITING)
    document = models.FileField(upload_to=upload_image_path, verbose_name='فایل تراکنش', null=True, blank=True)
    description = models.TextField(verbose_name='توضیحات', null=True, blank=True)
    user_receiver = models.ForeignKey('users.User', on_delete=models.CASCADE,
                                      related_name='transaction_history_user_receiver',
                                      verbose_name='کاربر دریافت کننده', null=True, blank=True)
    user_sender = models.ForeignKey('users.User', on_delete=models.CASCADE,
                                    related_name='transaction_history_user_sender',
                                    verbose_name='کاربر ارسال کننده', null=True, blank=True)

    class Meta:
        app_label = 'users'
