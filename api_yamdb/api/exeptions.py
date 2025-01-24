from rest_framework import status
from rest_framework.exceptions import APIException


class ValidationNameError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Validation Error"
    default_code = "validation_error"


class ValidationDublicateNotError(APIException):
    status_code = status.HTTP_200_OK
    default_detail = "Validation Error"
    default_code = "validation_error"
