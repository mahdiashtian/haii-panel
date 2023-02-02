from rest_framework.exceptions import APIException


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
