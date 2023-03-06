from django.db.models.signals import post_save
from django.dispatch import receiver

from teams.models import MemberRecruitmentFilter


@receiver(post_save, sender="teams.Team")
def create_team(sender, instance, created, **kwargs):
    if created:
        MemberRecruitmentFilter.objects.create(team=instance)
