import uuid

from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from utils.utils import upload_image_path, get_country_list


class ID(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class Child(ID):
    # profile :Inversely related to 'Child' from 'Profile'

    image = models.ImageField(upload_to=upload_image_path, verbose_name='تصویر شناسنامه')

    class Meta:
        app_label = 'users'


class Profile(ID):
    # ceo_team :Inversely related to 'Profile' from 'Team'
    # managers_team :Inversely related to 'Profile' from 'Team'
    # education :Inversely related to 'Profile' from 'Education'
    # skill :Inversely related to 'Profile' from 'Skill'
    # experience :Inversely related to 'Profile' from 'Experience'
    # team_user :Inversely related to 'Profile' from 'TeamUser'
    # iranian :Inversely related to 'Profile' from 'ProfileIranian'
    # foreign :Inversely related to 'Profile' from 'ProfileForeign'

    class GenderChoices(models.TextChoices):
        MAN = 'M', ('مرد')
        FEMALE = 'F', ('زن')

    class MaritalStatusChoices(models.TextChoices):
        MARRIED = 'M', ('متاهل')
        SINGLE = 'S', ('مجرد')

    class Condition(models.TextChoices):
        confirmed = 'C', ('تایید شده')
        pending = 'P', ('در انتظار تایید')
        rejected = 'R', ('رد شده')

    role = models.CharField(max_length=256, verbose_name='نقش کاربر')
    image = models.ImageField(upload_to=upload_image_path, verbose_name='تصویر پروفایل')
    is_confirmed = models.CharField(max_length=1, choices=Condition.choices, default=Condition.pending,
                                    verbose_name="تایید/عدم تایید حساب کاربری")
    country = models.CharField(max_length=4, choices=get_country_list(), verbose_name="کشور")
    date_of_birth = models.DateField(verbose_name="تاریخ تولد")
    child = models.ManyToManyField(Child, related_name='profile', blank=True, verbose_name='کودکان')
    phone_number = models.CharField(max_length=13,
                                    validators=[
                                        RegexValidator(
                                            regex='^(0)9(0[1-5]|[1 3]\d|2[0-2]|98)\d{7}$',
                                            message='شماره تلفن صحیح نیست',
                                            code='invalid_phone_number')
                                    ],
                                    verbose_name="شماره تلفن"
                                    )
    phone_verified = models.BooleanField(default=False, verbose_name="تایید/عدم تایید شماره تلفن")
    state = models.CharField(max_length=50, verbose_name="استان")
    city = models.CharField(max_length=50, verbose_name='نام شهر')
    address = models.CharField(max_length=150, verbose_name="آدرس")
    gender = models.CharField(max_length=25, choices=GenderChoices.choices, verbose_name='جنسیت')
    marital_status = models.CharField(max_length=25, choices=MaritalStatusChoices.choices, verbose_name='وضعیت تاهل')
    first_name = models.CharField(_("first name"), max_length=150, verbose_name='نام')
    last_name = models.CharField(_("last name"), max_length=150, verbose_name='نام خانوادگی')
    user = models.OneToOneField('User', on_delete=models.CASCADE, related_name='profile', verbose_name='کاربر')

    def get_full_name(self):
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        return self.first_name

    def __str__(self):
        return self.get_full_name()

    class Meta:
        app_label = 'users'


class ProfileIranian(ID):
    national_code = models.CharField(max_length=10, verbose_name="کد ملی")
    national_card_image = models.ImageField(upload_to=upload_image_path, verbose_name="تصویر کارت ملی")
    birth_certificate_image = models.ImageField(upload_to=upload_image_path, verbose_name="تصویر شناسنامه")
    profile = models.OneToOneField("users.Profile", on_delete=models.CASCADE, related_name='iranian',
                                   verbose_name='پروفایل')

    class Meta:
        app_label = 'users'


class ProfileForeigner(ID):
    passport_image = models.ImageField(upload_to=upload_image_path, verbose_name="تصویر پاسپورت")
    exclusive_code = models.CharField(max_length=12, verbose_name='کد اختصاصی')
    profile = models.OneToOneField("users.Profile", on_delete=models.CASCADE, related_name='foreigner',
                                   verbose_name='پروفایل', )

    class Meta:
        app_label = 'users'
