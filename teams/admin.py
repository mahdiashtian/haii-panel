from django.contrib import admin

from teams.models import Team, MemberRecruitmentFilter, Activity, MembershipRequest

admin.site.register(Team)
admin.site.register(MemberRecruitmentFilter)
admin.site.register(Activity)
admin.site.register(MembershipRequest)
# Register your models here.
