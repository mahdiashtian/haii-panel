import uuid

from django.db import models

from utils.utils import upload_image_path


class BaseInformationModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=255,
                            help_text='نام'
                            )

    description = models.TextField(
        help_text='توضیحات',
    )

    profile = models.ForeignKey('Profile', on_delete=models.CASCADE, related_name='%(class)s',
                                help_text='متصل کننده به مدل پروفایل')

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class Education(BaseInformationModel):
    class GradeChoices(models.TextChoices):
        CYCLE = 'CY', ('سیکل')
        DIPLOM = 'DI', ('دیپلم')
        KARSHENASI = 'MA', ('کارشناسی')
        KARSHENASI_ARSHAD = 'MP', ('کارشناسی ارشد')
        DOCTORA = 'DA', ('دکترا')

    major = models.CharField(max_length=255, help_text='رشته تحصیلی')

    grade = models.CharField(max_length=23, choices=GradeChoices.choices, help_text='مقطع تحصیلی')

    gpa = models.FloatField(help_text='معدل')

    image = models.ImageField(upload_to=upload_image_path, help_text='تصویر لوگو موسسه')

    start = models.DateField(help_text='تاریخ شروع')

    stop = models.DateField(help_text='تاریخ پایان')

    is_student = models.BooleanField(help_text='دانشجویی')

    class Meta:
        app_label = 'users'


class Skill(BaseInformationModel):
    class Meta:
        app_label = 'users'


class Experience(BaseInformationModel):
    image = models.ImageField(upload_to=upload_image_path, help_text='تصویر لوگو موسسه')

    company = models.CharField(max_length=255, help_text='نام شرکت')

    start = models.DateField(help_text='تاریخ شروع')

    stop = models.DateField(help_text='تاریخ پایان')

    class Meta:
        app_label = 'users'
