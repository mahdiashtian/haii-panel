from django.conf import settings
from rest_framework.exceptions import APIException

MINIMUM_YEAR = settings.MINIMUM_YEAR


class UserDoesNotExist(APIException):
    status_code = 400
    default_detail = 'کاربر مورد نظر وجود ندارد.'
    default_code = 'invalid'


class CreditAmountMustBePositive(APIException):
    status_code = 400
    default_detail = 'اعتبار باید بیشتر از صفر باشد.'
    default_code = 'invalid'


class CreditNotEnough(APIException):
    status_code = 400
    default_detail = 'اعتبار شما کافی نیست.'
    default_code = 'invalid'


class SelfCredit(APIException):
    status_code = 400
    default_detail = 'شما نمی توانید به خودتان اعتبار ارسال کنید.'
    default_code = 'invalid'


class NationalCodeInvalid(APIException):
    status_code = 400
    default_detail = 'کد ملی نامعتبر می باشد.'
    default_code = 'invalid'


class CannotHaveChild(APIException):
    status_code = 400
    default_detail = 'شما نمی توانید بچه داشته باشید.'
    default_code = 'invalid'


class NationalityDoseNoteMatch(APIException):
    status_code = 400
    default_detail = 'اطلاعات ملیتی با یک دیگر مطابقت ندارد.'
    default_code = 'invalid'


class AgeIsYounger(APIException):
    status_code = 400
    default_detail = f'حداقل سن برای ثبت نام {MINIMUM_YEAR} سال می باشد.'
    default_code = 'invalid'


class PasswordInvalid(APIException):
    status_code = 400
    default_detail = 'رمز عبور نامعتبر می باشد.'
    default_code = 'invalid'


class PhoneNumberInvalid(APIException):
    status_code = 400
    default_detail = 'شماره تلفن نامعتبر می باشد.'
    default_code = 'invalid'


class CodeInvalid(APIException):
    status_code = 400
    default_detail = 'کد نامعتبر می باشد.'
    default_code = 'invalid'


class SerializersException(APIException):
    status_code = 400
    default_detail = 'اطلاعات ارسالی نامعتبر است'
    default_code = 'invalid'
