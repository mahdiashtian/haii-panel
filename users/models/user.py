import uuid

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import UserManager, PermissionsMixin
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.mail import send_mail
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from utils.utils import upload_image_path, get_country_list


class IranianManager(UserManager):
    def get_queryset(self):
        return super().get_queryset().filter(profile__country='IR')


class ForeignerManager(UserManager):
    def get_queryset(self):
        return super().get_queryset().exclude(profile__country='IR')


class ID(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class AbstractUser(AbstractBaseUser, PermissionsMixin, ID):
    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        _("username"),
        max_length=150,
        unique=True,
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )

    email = models.EmailField(_("email address"), blank=True)

    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    objects = UserManager()

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def str(self):
        return self.username

    class Meta:
        default_manager_name = 'objects'
        base_manager_name = 'objects'
        abstract = True


class User(AbstractUser):
    credit = models.DecimalField(decimal_places=2,
                                 max_digits=11,
                                 verbose_name="اعتبار", default=0)
    iranian = IranianManager()
    foreigner = ForeignerManager()

    def role(self):
        if self.is_superuser:
            return 'مدیر کل'
        elif self.profile_user.team_ceo:
            return 'مدیر تیم'
        elif self.profile_user.team_manager:
            return 'هیات مدیره'
        else:
            return 'کاربر عادی'

    class Meta:
        default_manager_name = 'objects'
        base_manager_name = 'objects'
        app_label = 'users'


class ID(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class Children(ID):
    identification = models.ImageField(upload_to=upload_image_path, verbose_name='تصویر کارت ملی')


class Profile(ID):
    # team_ceo :Inversely related to 'Profile' from 'Team'
    # team_manager :Inversely related to 'Profile' from 'Team'
    # education_profile :Inversely related to 'Profile' from 'Education'
    # skill_profile :Inversely related to 'Profile' from 'Skill'
    # experience_profile :Inversely related to 'Profile' from 'Experience'
    # team_user_profile :Inversely related to 'Profile' from 'TeamUser'
    # iranian_profile :Inversely related to 'Profile' from 'ProfileIranian'
    # foreigner_profile :Inversely related to 'Profile' from 'ProfileForeign'

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

    title = models.CharField(max_length=256, verbose_name='نقش کاربر', null=True, blank=True)
    image = models.ImageField(upload_to=upload_image_path, verbose_name='تصویر پروفایل', null=True, blank=True)
    is_confirmed = models.CharField(max_length=1, choices=Condition.choices, default=Condition.pending,
                                    verbose_name="تایید/عدم تایید حساب کاربری", null=True, blank=True)
    country = models.CharField(max_length=4, choices=get_country_list(), verbose_name="کشور", null=True, blank=True)
    date_of_birth = models.DateField(verbose_name="تاریخ تولد", null=True, blank=True)
    phone_number = models.CharField(max_length=13,
                                    validators=[
                                        RegexValidator(
                                            regex='^(0)9(0[1-5]|[1 3]\d|2[0-2]|98)\d{7}$',
                                            message='شماره تلفن صحیح نیست',
                                            code='invalid_phone_number')
                                    ],
                                    verbose_name="شماره تلفن"
                                    , null=True, blank=True)
    phone_verified = models.BooleanField(default=False, verbose_name="تایید/عدم تایید شماره تلفن", null=True,
                                         blank=True)
    state = models.CharField(max_length=50, verbose_name="استان", null=True, blank=True)
    city = models.CharField(max_length=50, verbose_name='نام شهر', null=True, blank=True)
    address = models.CharField(max_length=150, verbose_name="آدرس", null=True, blank=True)
    gender = models.CharField(max_length=25, choices=GenderChoices.choices, verbose_name='جنسیت', null=True, blank=True)
    marital_status = models.CharField(max_length=25, choices=MaritalStatusChoices.choices, verbose_name='وضعیت تاهل',
                                      null=True, blank=True)
    first_name = models.CharField(_("first name"), max_length=150, null=True, blank=True)
    last_name = models.CharField(_("last name"), max_length=150, null=True, blank=True)
    user = models.OneToOneField('users.User', on_delete=models.CASCADE, related_name='profile_user',
                                verbose_name='کاربر', null=True, blank=True)
    iranian_profile = models.OneToOneField('users.Iranian', on_delete=models.SET_NULL, null=True, blank=True)
    foreigner_profile = models.OneToOneField('users.Foreigner', on_delete=models.SET_NULL, null=True, blank=True)
    childs = models.ManyToManyField(Children, verbose_name='فرزندان', null=True, blank=True)

    def get_full_name(self):
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        return self.first_name

    def __str__(self):
        return self.get_full_name()

    class Meta:
        app_label = 'users'


class Iranian(ID):
    national_code = models.CharField(max_length=10, verbose_name="کد ملی")
    national_card_image = models.ImageField(upload_to=upload_image_path, verbose_name="تصویر کارت ملی")
    birth_certificate_image = models.ImageField(upload_to=upload_image_path, verbose_name="تصویر شناسنامه")

    # profile = models.OneToOneField("users.Profile", on_delete=models.CASCADE, related_name='iranian_profile',
    #                                verbose_name='پروفایل')

    class Meta:
        app_label = 'users'


class Foreigner(ID):
    passport_image = models.ImageField(upload_to=upload_image_path, verbose_name="تصویر پاسپورت")
    exclusive_code = models.CharField(max_length=12, verbose_name='کد اختصاصی')

    # profile = models.OneToOneField("users.Profile", on_delete=models.CASCADE, related_name='foreigner_profile',
    #                                verbose_name='پروفایل', )

    class Meta:
        app_label = 'users'
