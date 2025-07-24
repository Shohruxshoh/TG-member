""" This module contains the schemas for the API documentation """

from drf_spectacular.utils import OpenApiResponse

from .enums import ErrorCodeEnum

DRFValidationErrorSchema = OpenApiResponse(
    response={
        "type": "object",
        "required": ["field_name"],
        "properties": {
            "field_name": {
                "type": "array",
                "items": {"type": "string"},
                "example": ["This field is required."],
            }
        },
        "example": {
            "email": ["This field is required."],
            "password": ["This field is required."],
        },
    },
    description="DRF validation error response",
)

ValidationErrorSchema = OpenApiResponse(
    response={
        "type": "object",
        "required": ["detail"],
        "properties": {
            "detail": {"type": "string", "example": "Validation error"},
            "error_code": {"type": "string", "example": "validation_error"},
        },
        "example": {"detail": "Validation error", "error_code": "validation_error"},
    },
    description="Validation error response",
)

NotFoundErrorSchema = OpenApiResponse(
    response={
        "type": "object",
        "required": ["detail"],
        "properties": {
            "detail": {"type": "string", "example": "Object not found"},
            "error_code": {"type": "string", "example": ErrorCodeEnum.NOT_FOUND.value},
        },
        "example": {
            "detail": "Object not found",
            "error_code": ErrorCodeEnum.NOT_FOUND.value,
        },
    },
    description="Not found error response",
)

AuthErrorSchema = OpenApiResponse(
    response={
        "type": "object",
        "required": ["detail"],
        "properties": {
            "detail": {"type": "string", "example": "Authentication failed"},
            "error_code": {
                "type": "string",
                "example": ErrorCodeEnum.AUTHENTICATION_FAILED.value,
            },
        },
        "example": {
            "detail": "Authentication failed",
            "error_code": ErrorCodeEnum.AUTHENTICATION_FAILED.value,
        },
    },
    description="Authentication error response",
)

PermissionErrorSchema = OpenApiResponse(
    response={
        "type": "object",
        "required": ["detail"],
        "properties": {
            "detail": {"type": "string", "example": "Permission denied"},
            "error_code": {
                "type": "string",
                "example": ErrorCodeEnum.PERMISSION_DENIED.value,
            },
        },
        "example": {
            "detail": "Permission denied",
            "error_code": ErrorCodeEnum.PERMISSION_DENIED.value,
        },
    },
    description="Permission error response",
)


AlreadyExistsErrorSchema = OpenApiResponse(
    response={
        "type": "object",
        "required": ["detail"],
        "properties": {
            "detail": {"type": "string", "example": "Already exists"},
            "error_code": {
                "type": "string",
                "example": ErrorCodeEnum.ALREADY_EXISTS.value,
            },
        },
        "example": {
            "detail": "Already exists",
            "error_code": ErrorCodeEnum.ALREADY_EXISTS.value,
        },
    },
    description="Permission error response",
)


COMMON_RESPONSES = {
    400: DRFValidationErrorSchema,
    401: AuthErrorSchema,
    422: ValidationErrorSchema,
    404: NotFoundErrorSchema,
    403: PermissionErrorSchema,
}
