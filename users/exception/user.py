from rest_framework.exceptions import APIException


class UserDoesNotExist(APIException):
    status_code = 400
    default_detail = 'User does not exist'
    default_code = 'invalid'


class CreditAmountMustBePositive(APIException):
    status_code = 400
    default_detail = 'Amount must be positive'
    default_code = 'invalid'


class CreditNotEnough(APIException):
    status_code = 400
    default_detail = 'Credit not enough'
    default_code = 'invalid'


class SelfCredit(APIException):
    status_code = 400
    default_detail = 'You cannot send credit to yourself'
    default_code = 'invalid'
