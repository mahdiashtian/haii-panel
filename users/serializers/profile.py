import uuid

from django.conf import settings
from django.core.cache import cache
from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers

from users.exception import AgeIsYounger
from users.models import Profile, Foreigner, Iranian, User, Children
from users.serializers import SkillSerializer, EducationSerializer, ExperienceSerializer, UserSerializer
from users.validators import CodeMelliValidator, ProfileValidator

MINIMUM_YEAR = settings.MINIMUM_YEAR


class IranianSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(required=False)

    def validate_national_code(self, value):
        value = str(value)
        validator = CodeMelliValidator()
        return validator.validate(value)

    class Meta:
        model = Iranian
        fields = '__all__'


class ForeignerSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(required=False)

    class Meta:
        model = Foreigner
        fields = '__all__'


class ChildrenSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(required=False)

    class Meta:
        model = Children
        fields = '__all__'


class ProfileSerializer(WritableNestedModelSerializer):
    iranian_profile = IranianSerializer(required=False)
    foreigner_profile = ForeignerSerializer(required=False)
    childs = ChildrenSerializer(many=True, required=False)
    skill_profile = SkillSerializer(many=True, read_only=True)
    education_profile = EducationSerializer(many=True, read_only=True)
    experience_profile = ExperienceSerializer(many=True, read_only=True)
    user = UserSerializer(required=False)
    clear_childs = serializers.BooleanField(write_only=True, required=False)

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        ex = kwargs.pop('ex', None)
        super().__init__(*args, **kwargs)

        if fields and ex is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

        for field in self.fields:
            if field not in self.Meta.exempt_fields:
                self.fields[field].required = True

        super().__init__(*args, **kwargs)

    def update(self, instance, validated_data):
        childs = validated_data.pop('childs', None)
        clear_childs = validated_data.pop('clear_childs', None)
        if clear_childs:
            instance.childs.all().delete()
        if childs:
            for child in childs:
                if not child.get('id', None):
                    print("not iud")
                    child['id'] = uuid.uuid4()
        print(childs)
        # add childid in validated data
        user = self.context['request'].user
        if user.is_superuser:
            instance.is_confirmed = "C"
        else:
            instance.is_confirmed = "P"

        validated_data_dict = dict(validated_data)
        iranian = getattr(instance, 'iranian_profile', None)
        foreigner = getattr(instance, 'foreigner_profile', None)

        if iranian and not validated_data_dict.get('iranian_profile_id', None):
            instance.iranian_profile.delete()
            instance.iranian_profile = None
        if foreigner and not validated_data_dict.get('foreigner_profile_id', None):
            instance.foreigner_profile.delete()
            instance.foreigner_profile = None

        phone_chache = cache.get(f"phone-{str(user.id)}")
        if phone_chache:
            cache.delete(f"phone-{str(user.id)}")
            phone = phone_chache.get('phone')
            verified = phone_chache.get('verified')
            if verified and phone == validated_data.get('phone_number', None):
                instance.phone_verified = True
            else:
                instance.phone_verified = False
        else:
            if instance.phone_number != validated_data.get('phone_number', None):
                instance.phone_verified = False
        instance = super().update(instance, validated_data)
        if childs:
            obj = [Children.objects.get_or_create(id=i['id'], defaults=i)[0] for i in childs]
            instance.childs.set(obj)
        return instance

    def validate(self, attrs):
        validator = ProfileValidator()
        return validator.validate(attrs, self.context['request'])

        return attrs

    def validate_date_of_birth(self, value):
        year = value.year
        minimum_year = value.today().year - MINIMUM_YEAR
        if minimum_year <= year:
            raise AgeIsYounger
        return value

    class Meta:
        model = Profile
        fields = (
            'id', 'first_name', 'last_name', 'user', 'marital_status', 'gender', 'address', 'city', 'state',
            'phone_verified', 'phone_number', 'childs', 'date_of_birth', 'country', 'is_confirmed', 'image', 'role',
            'iranian_profile', 'foreigner_profile', 'skill_profile', 'education_profile', 'experience_profile',
            'clear_childs'
        )
        read_only_fields = ('id', 'is_confirmed', 'phone_verified')
        exempt_fields = ['user', 'iranian_profile', 'foreigner_profile','childs']


class ConfirmProfileSerializer(serializers.Serializer):
    profile_ids = serializers.ListField(child=serializers.UUIDField(), required=True, allow_null=False)
    condition = serializers.ChoiceField(choices=Profile.Condition.choices, allow_null=False, required=True)
    reason = serializers.CharField(allow_null=True, required=False)


class ChangePasswordSerializer(serializers.Serializer):
    model = User
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    re_new_password = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['re_new_password']:
            raise serializers.ValidationError('New password and re new password are not equal.')
        return attrs
