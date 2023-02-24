from codemelli import validator
from django.conf import settings

from users.exception import NationalCodeInvalid, CannotHaveChild, NationalityDoseNoteMatch

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

        return attrs
