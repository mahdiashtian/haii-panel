from codemelli import validator
from django.conf import settings

from users.exception import NationalCodeInvalid, CannotHaveChild, NationalityDoseNoteMatch, CityDoesNotExist
from utils.cities import check_city, check_province

MINIMUM_YEAR = settings.MINIMUM_YEAR


class CodeMelliValidator(object):
    def validate(self, value, **kwargs):
        if validator(value) and len(value) == 10:
            return value

        return NationalCodeInvalid


class ProfileValidator(object):

    def validate(self, attrs, request, **kwargs):
        martial_status = attrs.get('marital_status', None)
        child = attrs.get('child', None)
        country = attrs.get('country', None)
        iranian = attrs.get('iranian_profile', None)
        foreigner = attrs.get('foreigner_profile', None)
        city = check_city(attrs.get('city', None))
        state = check_province(attrs.get('state', None))

        if city['province_id'] != state['id']:
            raise CityDoesNotExist

        if martial_status != 'M' and child:
            raise CannotHaveChild

        if country == 'IR' and not iranian:
            raise NationalityDoseNoteMatch

        if country != 'IR' and not foreigner:
            raise NationalityDoseNoteMatch

        if not foreigner and not iranian:
            raise NationalityDoseNoteMatch

        if foreigner and iranian:
            raise NationalityDoseNoteMatch

        attrs['city'] = city['name']
        attrs['state'] = state['name']
        return attrs
