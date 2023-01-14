from rest_framework import status
from rest_framework.exceptions import APIException


class MaximumSkill(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'شما نمی توانید بیشتر از ۳ مهارت داشته باشید'
    default_code = 'invalid'

