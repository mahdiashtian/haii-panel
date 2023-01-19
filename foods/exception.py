from rest_framework import status
from rest_framework.exceptions import APIException


class DateIsPast(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'تاریخ انتخاب شده قبل از امروز است.'
    default_code = 'date_is_past'
