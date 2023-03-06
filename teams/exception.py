from rest_framework.exceptions import APIException


class MaxParentDepthExceeded(APIException):
    status_code = 400
    default_detail = 'تعداد زیر مجموعه به حداکثر رسیده است.'
    default_code = 'max_parent_depth_exceeded'