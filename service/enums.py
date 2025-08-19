from django.db.models.enums import StrEnum
from django.db import models

class ErrorCodeEnum(StrEnum):
    """
    Custom error codes for response.

    Example:
        raise CustomAPIException(
            status_code=422,
            detail="Validation error",
            error_code=ErrorCodeEnum.VALIDATION_ERROR
        )
    Add new error codes if needed.
    """

    INTERNAL_SERVER_ERROR = "internal_server_error"
    VALIDATION_ERROR = "validation_error"
    AUTHENTICATION_FAILED = "authentication_failed"
    PERMISSION_DENIED = "permission_denied"
    NOT_FOUND = "not_found"
    ALREADY_EXISTS = "already_exists"
    ALREADY_PAID = "already_paid"
    INVALID_ORIGIN = "invalid_origin"

class Category(models.TextChoices):
    PREMIUM = "PREMIUM", "Premium"
    VIEW = "VIEW", "View"
    REACTION = "REACTION", "Reaction"
    MEMBER = "MEMBER", "Member"

