""" The file for writing exceptions """

from rest_framework.exceptions import APIException
from .enums import ErrorCodeEnum


class CustomAPIException(APIException):
    """
    Custom API Exception

    Example:
        raise CustomAPIException(
            status_code=400,
            detail="Validation error",
            error_code=ErrorCodeEnum.VALIDATION_ERROR
        )

    Use this error schema with error_code, because
    error_code will be used in the frontend.
    Frontend will handle the error based on the error_code.
    """

    def __init__(
        self,
        detail: str,
        error_code: str = ErrorCodeEnum.INTERNAL_SERVER_ERROR.value,
        status_code: int = 500,
    ):
        self.status_code = status_code
        self.detail = detail
        self.error_code = error_code
        self.message = detail
        super().__init__({"detail": detail, "error_code": error_code})
