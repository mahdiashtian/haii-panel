from rest_framework import status
from rest_framework.exceptions import APIException


class DateIsPast(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'به دلیل گذشت زمان شما اجازه انجام این کار را ندارید.'
    default_code = 'date_is_past'


class NotEnoughMoney(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'موجودی شما کافی نیست.'
    default_code = 'not_enough_money'


class FoodAndDesireIsNotValid(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'لطفا غذا را انتخاب کنید.'
    default_code = 'food_and_desire_is_not_valid'


class PermissionDenied(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'شما دسترسی مشاهده این صفحه را ندارید.'
    default_code = 'permission_denied'


class InputNotValid(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'ورودی ارسالی نامعتبر می باشد.'
    default_code = 'invalid'


class LimitFoodAndDesire(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'مقادیر ارسالی بیش از حد مجاز است.'
    default_code = 'invalid'


class LimitMeal(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'شما از قبل وعده غذایی خودرا در تاریخ مورد نظر انتخاب کرده اید.'
    default_code = 'invalid'
