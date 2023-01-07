import uuid

from django.db import models

from utils.utils import upload_image_path


class ID(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class Team(ID):
    # activity :Inversely related to 'Team' from 'Activity'
    # team_user :Inversely related to 'Team' from 'TeamUser'

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
