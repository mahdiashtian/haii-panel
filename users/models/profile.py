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
    # profile :Inversely related to 'Child'
    image = models.ImageField(upload_to=upload_image_path, help_text='تصویر کودک')

    class Meta:
        app_label = 'users'


class Profile(ID):
    # foreigner :Inversely related to 'Profile'

    # iranian :Inversely related to 'Profile'

    # Education :Inversely related to 'Profile'

    # Skill :Inversely related to 'Profile'

    # Experience :Inversely related to 'Profile'

    image = models.ImageField(upload_to=upload_image_path, help_text='تصویر پروفایل')

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

    role = models.CharField(max_length=256, help_text='نقش کاربر در سایت')

    is_confirmed = models.CharField(max_length=1, choices=Condition.choices, default=Condition.pending,
                                    help_text="تایید حساب کاربری")

    country = models.CharField(max_length=4, choices=get_country_list(), help_text="کشور")

    date_of_birth = models.DateField(help_text="تاریخ تولد")

    child = models.ManyToManyField(Child, related_name='profile', blank=True,
                                   help_text="فیلد متصل کننده بچه پدر یا مادر")

    phone_number = models.CharField(max_length=13,
                                    validators=[
                                        RegexValidator(
                                            regex='^(0)9(0[1-5]|[1 3]\d|2[0-2]|98)\d{7}$',
                                            message='شماره تلفن صحیح نیست',
                                            code='invalid_phone_number')
                                    ],
                                    help_text="شماره تلفن"
                                    )

    phone_verified = models.BooleanField(default=False, help_text="تایید شماره تلفن")

    state = models.CharField(max_length=50, help_text="استان")

    city = models.CharField(max_length=50, help_text='نام شهر')

    address = models.CharField(max_length=150, help_text="آدرس")

    gender = models.CharField(max_length=25, choices=GenderChoices.choices, help_text='جنسیت')

    marital_status = models.CharField(max_length=25, choices=MaritalStatusChoices.choices, help_text='وضعیت تاهل')

    first_name = models.CharField(_("first name"), max_length=150, help_text='نام')

    last_name = models.CharField(_("last name"), max_length=150, help_text='نام خانوادگی')

    user = models.OneToOneField('User', on_delete=models.CASCADE, related_name='profile',
                                help_text="فیلد متصل کننده پروفایل به کاربر خاص")

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
    national_code = models.CharField(max_length=10, help_text="کد ملی")
    national_card_image = models.ImageField(upload_to=upload_image_path, help_text="تصویر کارت ملی")
    birth_certificate_image = models.ImageField(upload_to=upload_image_path, help_text="تصویر شناسنامه")
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name='iranian',
                                   help_text="فیلد متصل کننده پروفایل ایرانی به پروفایل")

    class Meta:
        app_label = 'users'


class ProfileForeigner(ID):
    passport_image = models.ImageField(upload_to=upload_image_path, help_text="تصویر پاسپورت")
    exclusive_code = models.CharField(max_length=12, help_text='کد اختصاصی')
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name='foreigner',
                                   help_text="فیلد متصل کننده پروفایل خارجی به پروفایل")

    class Meta:
        app_label = 'users'
