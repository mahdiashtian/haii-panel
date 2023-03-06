import uuid
import warnings

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.functional import cached_property
from rest_framework import serializers

from main.melipayamak import Api
from teams.exception import MaxParentDepthExceeded
from teams.models import Team, Activity, MemberRecruitmentFilter, MembershipRequest
from users.models import TeamUser

username = settings.SMS_USERNAME
password = settings.SMS_PASSWORD
from_ = settings.SMS_FROM
api = Api(username, password)
sms = api.sms()
User = get_user_model()


class DynamicFieldsMixin(object):
    """
    A serializer mixin that takes an additional `fields` argument that controls
    which fields should be displayed.
    """

    @cached_property
    def fields(self):
        """
        Filters the fields according to the `fields` query parameter.

        A blank `fields` parameter (?fields) will remove all fields. Not
        passing `fields` will pass all fields individual fields are comma
        separated (?fields=id,name,url,email).

        """
        fields = super(DynamicFieldsMixin, self).fields

        if not hasattr(self, "_context"):
            # We are being called before a request cycle
            return fields

        # Only filter if this is the root serializer, or if the parent is the
        # root serializer with many=True
        is_root = self.root == self
        parent_is_list_root = self.parent == self.root and getattr(
            self.parent, "many", False
        )
        if not (is_root or parent_is_list_root):
            return fields

        try:
            request = self.context["request"]

        except KeyError:
            conf = getattr(settings, "DRF_DYNAMIC_FIELDS", {})
            if not conf.get("SUPPRESS_CONTEXT_WARNING", False) is True:
                warnings.warn(
                    "Context does not have access to request. "
                    "See README for more information."
                )
            return fields

        # NOTE: drf test framework builds a request object where the query
        # parameters are found under the GET attribute.
        params = getattr(self, "params", None)
        if params:

            try:
                filter_fields = params.get("fields", None)
            except AttributeError:
                filter_fields = None

            try:
                omit_fields = params.get("omit", None)
            except AttributeError:
                omit_fields = []

            existing = set(fields.keys())
            if filter_fields is None:
                allowed = existing
            else:
                allowed = set(filter(None, filter_fields))

            for field in existing:

                if field not in allowed:
                    fields.pop(field, None)

        return fields


class ActivitySerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['child'] = ActivitySerializer(instance.activity_parent.all(), many=True).data
        return data

    def validated_parent(self, value):
        def get_depth(value):
            if value.parent is None:
                return 0
            return get_depth(value.parent) + 1

        max_depth = 3
        for sub_category in value:
            depth = get_depth(sub_category)
            if depth > max_depth:
                raise MaxParentDepthExceeded
        return value

    class Meta:
        model = Activity
        fields = '__all__'


class TeamSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    activity_team = ActivitySerializer(many=True, read_only=True)
    team_members = serializers.CharField(source='members', read_only=True)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['ceo'] = serializers.StringRelatedField().to_representation(instance.ceo)
        data['managers'] = serializers.StringRelatedField(many=True).to_representation(instance.managers.all())
        return data

    def create(self, validated_data):
        ceo = validated_data.get('ceo')
        managers = validated_data.get('managers', None)

        if ceo not in managers:
            managers.append(ceo)

        validated_data['managers'] = managers
        instance = super().create(validated_data)
        TeamUser.objects.bulk_create(
            [TeamUser(profile=profile, team=instance, membership_type="PE") for profile in managers]
        )
        return instance

    def update(self, instance, validated_data):
        user = self.context['request'].user
        if not user.is_superuser:
            validated_data.pop('is_confirmed', None)
            instance.is_confirmed = 'P'
        return super().update(instance, validated_data)

    class Meta:
        model = Team
        fields = '__all__'


class MemberRecruitmentFilterSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['activity'] = ActivitySerializer(instance.activity.all(), many=True).data
        data['team'] = TeamSerializer(instance.team).data

        return data

    class Meta:
        model = MemberRecruitmentFilter
        fields = '__all__'


class MembershipRequestSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        team = attrs.get('team', None)
        team_recuitment_filter = getattr(team, "member_recruitment_filter_team", None)
        if team_recuitment_filter:
            if team_recuitment_filter.age:
                if not team_recuitment_filter.age[0] < attrs.get('age', None) < team_recuitment_filter.age[1]:
                    raise serializers.ValidationError("Age is not valid")
            if team_recuitment_filter.experience:
                if not team_recuitment_filter.experience[0] < attrs.get('experience', None) < \
                       team_recuitment_filter.experience[1]:
                    raise serializers.ValidationError("Experience is not valid")
            if team_recuitment_filter.activity:
                activity = attrs.get('activity', None)
                if activity:
                    for i in activity:
                        if i not in team_recuitment_filter.activity.all():
                            raise serializers.ValidationError("Activity is not valid")
            if team_recuitment_filter.gender:
                if attrs.get('gender', None) != team_recuitment_filter.gender:
                    raise serializers.ValidationError("gender is not valid")
            if team_recuitment_filter.membership_type:
                if attrs.get('membership_type', None) != team_recuitment_filter.membership_type:
                    raise serializers.ValidationError("Membership type is not valid")
            if team_recuitment_filter.city:
                if attrs.get('city', None) != team_recuitment_filter.city:
                    raise serializers.ValidationError("City is not valid")

        return attrs

    def create(self, validated_data):
        instance = super().create(validated_data)
        instance.is_confirmed = 'P'
        instance.save()
        return instance

    def update(self, instance, validated_data):
        is_confirmed = validated_data.get('is_confirmed', None)
        if is_confirmed == 'C':
            username = 'user' + str(uuid.uuid4())[:8]
            password = 'pass' + str(uuid.uuid4())[:8]
            user = User.objects.create_user(username=username, password=password)
            TeamUser.objects.create(profile=user.profile_user, team=instance.team,
                                    membership_type=instance.membership_type)
            result = sms.send(instance.phone_number, from_,
                              "Your username is " + username + " and password is " + password)
        elif is_confirmed == 'R':
            result = sms.send(instance.phone_number, from_,
                              "Your request has been rejected")
        return super().update(instance, validated_data)

    class Meta:
        model = MembershipRequest
        fields = '__all__'
        exempt_fields = ['is_confirmed', 'activity']
