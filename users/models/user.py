import uuid

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import UserManager, PermissionsMixin
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


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
    # profile_user :Inversely related to 'User' from 'Profile'
    # payment_food_user :Inversely related to 'User' from 'PaymentFood'
    # transaction_history_user_receiver :Inversely related to 'User' from 'TransactionHistory'
    # transaction_history_user_sender :Inversely related to 'User' from 'TransactionHistory'

    credit = models.DecimalField(decimal_places=2,
                                 max_digits=11,
                                 verbose_name="اعتبار", default=0)
    iranian = IranianManager()
    foreigner = ForeignerManager()

    class Meta:
        default_manager_name = 'objects'
        base_manager_name = 'objects'
        app_label = 'users'
