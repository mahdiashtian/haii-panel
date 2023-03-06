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
    # activity_team :Inversely related to 'Team' from 'Activity'
    # team_user_team :Inversely related to 'Team' from 'TeamUser'
    # membership_request_team :Inversely related to 'Team' from 'MembershipRequest'
    # member_recruitment_filter_team :Inversely related to 'Team' from 'MemberRecruitmentFilter'
    class Condition(models.TextChoices):
        confirmed = 'C', ('تایید شده')
        pending = 'P', ('در انتظار تایید')
        rejected = 'R', ('رد شده')

    name = models.CharField(max_length=256, verbose_name="نام تیم")
    description = models.TextField(verbose_name="توضیحات")
    managers = models.ManyToManyField("users.Profile", related_name='team_manager', verbose_name="مدیران تیم",
                                      limit_choices_to={"team_manager": None}, blank=True
                                      )
    ceo = models.ForeignKey("users.Profile", on_delete=models.CASCADE, related_name='team_ceo',
                            verbose_name="مدیر عامل", limit_choices_to={"team_ceo": None},
                            )
    create_date = models.DateTimeField(verbose_name="تاریخ ایجاد")
    image = models.ImageField(upload_to=upload_image_path, verbose_name='تصویر تیم')
    is_confirmed = models.CharField(max_length=1, choices=Condition.choices, default=Condition.pending,
                                    verbose_name="تایید/عدم تایید ")

    def members(self):
        return self.team_user_team.all().count()

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'teams'


class Activity(ID):
    # activity_parent :Inversely related to 'Activity' from 'Activity'
    # membership_request_activity :Inversely related to 'Activity' from 'MembershipRequest'
    # member_recruitment_filter_activity :Inversely related to 'Activity' from 'MemberRecruitmentFilter'

    name = models.CharField(max_length=256, verbose_name='نام فعالیت')
    description = models.TextField(verbose_name='توضیحات فعالیت')
    image = models.ImageField(upload_to=upload_image_path, verbose_name='تصویر فعالیت')
    child = models.ForeignKey("self", on_delete=models.CASCADE, related_name='activity_parent', null=True, blank=True,
                              verbose_name='ریشه فعالیت')
    team = models.ForeignKey("teams.Team", on_delete=models.CASCADE, null=True, blank=True,
                             related_name='activity_team',
                             verbose_name='تیم مربوطه')

    def __str__(self):
        return self.name

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
        MaxValueValidator(50)]), verbose_name='سن', size=2, null=True, blank=True)
    experience = ArrayField(models.PositiveSmallIntegerField(validators=[
        MinValueValidator(1),
        MaxValueValidator(50)]), verbose_name='سابقه', size=2, null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GenderChoices.choices, verbose_name='جنسیت', null=True, blank=True)
    city = models.CharField(max_length=256, verbose_name='شهر', null=True, blank=True)
    membership_type = models.CharField(max_length=2, choices=MembershipChoices.choices, verbose_name='نوع عضویت',
                                       null=True, blank=True)
    team = models.OneToOneField("teams.Team", on_delete=models.CASCADE, related_name='member_recruitment_filter_team',
                                verbose_name='تیم مربوطه')
    activity = models.ManyToManyField("teams.Activity", related_name='member_recruitment_filter_activity',
                                      verbose_name='فعالیت مربوطه', blank=True, null=True)

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

    class Condition(models.TextChoices):
        confirmed = 'C', ('تایید شده')
        pending = 'P', ('در انتظار تایید')
        rejected = 'R', ('رد شده')

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
    team = models.ForeignKey("teams.Team", on_delete=models.CASCADE, related_name='membership_request_team',
                             verbose_name='تیم مربوطه')
    cv = models.FileField(upload_to=upload_image_path, verbose_name='رزومه')
    is_confirmed = models.CharField(max_length=1, choices=Condition.choices, default=Condition.pending,
                                    verbose_name="تایید/عدم تایید", null=True, blank=True)
    description = models.TextField(verbose_name='توضیحات')
    activity = models.ManyToManyField("teams.Activity", related_name='membership_request_activity',
                                      verbose_name='بخش های فعالیت',blank=True)

    def __str__(self):
        return self.full_name

    class Meta:
        app_label = 'teams'
