import uuid

from django.contrib.postgres.fields import ArrayField
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.db import models

from utils.utils import upload_image_path


class ID(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class Team(ID):
    # activity :Inversely related to 'Team' from 'Activity'
    # team_user :Inversely related to 'Team' from 'TeamUser'
    # membership_request :Inversely related to 'Team' from 'MembershipRequest'
    # member_recruitment_filter :Inversely related to 'Team' from 'MemberRecruitmentFilter'

    name = models.CharField(max_length=256, verbose_name="نام تیم")
    description = models.TextField(verbose_name="توضیحات")
    managers = models.ManyToManyField("users.Profile", related_name='managers_team', verbose_name="مدیران تیم")
    ceo = models.ForeignKey("users.Profile", on_delete=models.SET_NULL, related_name='ceo_team',
                            verbose_name="مدیر عامل")

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'teams'


class Activity(ID):
    # children :Inversely related to 'Activity' from 'Activity'
    # membership_request :Inversely related to 'Activity' from 'MembershipRequest'
    # member_recruitment_filter :Inversely related to 'Activity' from 'MemberRecruitmentFilter'

    name = models.CharField(max_length=256, verbose_name='نام فعالیت')
    description = models.TextField(verbose_name='توضیحات فعالیت')
    image = models.ImageField(upload_to=upload_image_path, verbose_name='تصویر فعالیت')
    parent = models.ForeignKey("self", on_delete=models.CASCADE, related_name='children', null=True, blank=True,
                               verbose_name='ریشه فعالیت')
    team = models.ForeignKey("teams.Team", on_delete=models.CASCADE, null=True, blank=True, related_name='activity',
                             verbose_name='تیم مربوطه')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.parent:
            self.team = None
        super().save(*args, **kwargs)

    class Meta:
        app_label = 'teams'


class MemberRecruitmentFilter(ID):
    class GenderChoices(models.TextChoices):
        MAN = 'M', ('مرد')
        FEMALE = 'F', ('زن')

    class MembershipChoices(models.TextChoices):
        PERMANENT = 'PE', ('دائمی')
        FREELANCER = 'FR', ('فریلنسر')
        LEARNER = 'LE', ('کارآموز')

    age = ArrayField(models.PositiveSmallIntegerField(validators=[
        MinValueValidator(1),
        MaxValueValidator(50)]), verbose_name='سن', size=2)
    experience = ArrayField(models.PositiveSmallIntegerField(validators=[
        MinValueValidator(1),
        MaxValueValidator(50)]), verbose_name='سابقه', size=2)
    gender = models.CharField(max_length=1, choices=GenderChoices.choices, verbose_name='جنسیت')
    city = models.CharField(max_length=256, verbose_name='شهر')
    membership_type = models.CharField(max_length=2, choices=MembershipChoices.choices, verbose_name='نوع عضویت')
    team = models.OneToOneField("teams.Team", on_delete=models.CASCADE, related_name='member_recruitment_filter',
                                verbose_name='تیم مربوطه')
    activity = models.ManyToManyField("teams.Activity", related_name='member_recruitment_filter',
                                      verbose_name='فعالیت مربوطه')

    def __str__(self):
        return self.id

    class Meta:
        app_label = 'teams'


class MembershipRequest(ID):
    class GenderChoices(models.TextChoices):
        MAN = 'M', ('مرد')
        FEMALE = 'F', ('زن')

    class MembershipChoices(models.TextChoices):
        PERMANENT = 'PE', ('دائمی')
        FREELANCER = 'FR', ('فریلنسر')
        LEARNER = 'LE', ('کارآموز')

    full_name = models.CharField(max_length=256, verbose_name='نام و نام خانوادگی')
    phone_number = models.CharField(max_length=13,
                                    validators=[
                                        RegexValidator(
                                            regex='^(0)9(0[1-5]|[1 3]\d|2[0-2]|98)\d{7}$',
                                            message='شماره تلفن صحیح نیست',
                                            code='invalid_phone_number')
                                    ],
                                    verbose_name="شماره تلفن"
                                    )
    experience = models.PositiveSmallIntegerField(verbose_name='سابقه کاری')
    age = models.PositiveSmallIntegerField(verbose_name='سن')
    gender = models.CharField(max_length=1, choices=GenderChoices.choices, verbose_name='جنسیت')
    city = models.CharField(max_length=256, verbose_name='شهر')
    membership_type = models.CharField(max_length=2, choices=MembershipChoices.choices, verbose_name='نوع عضویت')
    team = models.ForeignKey("teams.Team", on_delete=models.CASCADE, related_name='membership_request',
                             verbose_name='تیم مربوطه')
    cv = models.FileField(upload_to=upload_image_path, verbose_name='رزومه')
    status = models.BooleanField(default=False, verbose_name='رد/تایید شده')
    description = models.TextField(verbose_name='توضیحات')
    activity = models.ManyToManyField("teams.Activity", related_name='membership_request',
                                      verbose_name='بخش های فعالیت')

    def __str__(self):
        return self.full_name

    class Meta:
        app_label = 'teams'
