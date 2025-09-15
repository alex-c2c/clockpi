from enum import Enum
from logging import Logger, getLogger
from typing import NoReturn

from flask import g
from flask_restx import abort, fields
from flask_restx._http import HTTPStatus
from msgspec import Raw

from app import api

logger: Logger = getLogger(__name__)


class ErrorCode(str, Enum):
	# Authentication & Authorization
	AUTHENTICATION_FAILED = "AUTHENTICATION_FAILED"
	TOKEN_EXPIRED = "TOKEN_EXPIRED"
	FORBIDDEN = "FORBIDDEN"
	INSUFFICIENT_SCOPE = "INSUFFICIENT_SCOPE"

	# Client Input / Validation
	INVALID_INPUT = "INVALID_INPUT"
	VALIDATION_ERROR = "VALIDATION_ERROR"
	MISSING_REQUIRED_FIELD = "MISSING_REQUIRED_FIELD"
	INVALID_DEPENDENCY = "INVALID_DEPENDENCY"
	CONFLICT = "CONFLICT"

	# Resource / Not Found
	RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
	USER_NOT_FOUND = "USER_NOT_FOUND"
	DEVICE_NOT_FOUND = "DEVICE_NOT_FOUND"
	SCHEDULE_NOT_FOUND = "SCHEDULE_NOT_FOUND"
	WALLPAPER_NOT_FOUND = "WALLPAPER_NOT_FOUND"

	# Server / Internal Errors
	INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
	SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
	DATABASE_ERROR = "DATABASE_ERROR"

	# Rate Limiting / Quotas
	RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
	QUOTA_EXCEEDED = "QUOTA_EXCEEDED"

	# Optional / Misc
	NOT_IMPLEMENTED = "NOT_IMPLEMENTED"
	UNSUPPORTED_MEDIA_TYPE = "UNSUPPORTED_MEDIA_TYPE"
	UNPROCESSABLE_ENTITY = "UNPROCESSABLE_ENTITY"


ERROR_CONFIG = {
	ErrorCode.AUTHENTICATION_FAILED: (HTTPStatus.UNAUTHORIZED, "Invalid username or password."),
	ErrorCode.TOKEN_EXPIRED: (HTTPStatus.UNAUTHORIZED, "Authentication token has expired."),
	ErrorCode.FORBIDDEN: (HTTPStatus.FORBIDDEN, "You do not have permission to perform this action."),
	ErrorCode.INSUFFICIENT_SCOPE: (HTTPStatus.FORBIDDEN, "Your token does not have sufficient permissions."),

	# Validation / Input
	ErrorCode.INVALID_INPUT: (HTTPStatus.BAD_REQUEST, "One or more fields are invalid."),
	ErrorCode.VALIDATION_ERROR: (HTTPStatus.BAD_REQUEST, "One or more fields failed validation."),
	ErrorCode.MISSING_REQUIRED_FIELD: (HTTPStatus.BAD_REQUEST, "A required property is missing."),
	ErrorCode.INVALID_DEPENDENCY: (HTTPStatus.BAD_REQUEST, "A referenced dependency does not exist."),
	ErrorCode.CONFLICT: (HTTPStatus.CONFLICT, "Resource already exists or conflicts with existing data."),

	# Not Found
	ErrorCode.RESOURCE_NOT_FOUND: (HTTPStatus.NOT_FOUND, "Requested resource does not exist."),
	ErrorCode.USER_NOT_FOUND: (HTTPStatus.NOT_FOUND, "User not found."),
	ErrorCode.DEVICE_NOT_FOUND: (HTTPStatus.NOT_FOUND, "Device not found."),
	ErrorCode.SCHEDULE_NOT_FOUND: (HTTPStatus.NOT_FOUND, "Schedule not found."),
	ErrorCode.WALLPAPER_NOT_FOUND: (HTTPStatus.NOT_FOUND, "Wallpaper not found."),

	# Server
	ErrorCode.INTERNAL_SERVER_ERROR: (HTTPStatus.INTERNAL_SERVER_ERROR, "An unexpected server error occurred."),
	ErrorCode.SERVICE_UNAVAILABLE: (HTTPStatus.SERVICE_UNAVAILABLE, "The service is temporarily unavailable."),
	ErrorCode.DATABASE_ERROR: (HTTPStatus.INTERNAL_SERVER_ERROR, "A database error occurred."),

	# Rate Limiting
	ErrorCode.RATE_LIMIT_EXCEEDED: (HTTPStatus.TOO_MANY_REQUESTS, "Too many requests. Please try again later."),
	ErrorCode.QUOTA_EXCEEDED: (HTTPStatus.TOO_MANY_REQUESTS, "Your quota has been exceeded."),

	# Misc
	ErrorCode.NOT_IMPLEMENTED: (HTTPStatus.NOT_IMPLEMENTED, "This feature is not implemented."),
	ErrorCode.UNSUPPORTED_MEDIA_TYPE: (HTTPStatus.UNSUPPORTED_MEDIA_TYPE, "The request content type is not supported."),
	ErrorCode.UNPROCESSABLE_ENTITY: (HTTPStatus.UNPROCESSABLE_ENTITY, "Entity is unprocessable.")
}


STANDARD_ERRORS = {
	code: {
		"status": status,
		"error_code": code.value,
		"default_message": message
	}
	
	for code, (status, message) in ERROR_CONFIG.items()
}


error_fields = api.model("Error", {
	"errorCode": 	fields.String(description="Error code", required=True),
	"message":		fields.String(description="Error message", required=True),
	"requestId": 	fields.String(description="Request ID", required=True),
	"detail": 		fields.String(description="Detailed message"),
	"fields": 		fields.Raw(description="Arbitrary dictionary [str, any] about offending input fields"),
})


def api_abort(error_code: ErrorCode, **kwargs) -> NoReturn:
	#logger.debug(f"{error_code=} {kwargs=}")
	err = STANDARD_ERRORS[error_code]
	kwargs["requestId"] = getattr(g, "request_id", None)
	kwargs["errorCode"] = err["error_code"]
	abort(err["status"].value, err["default_message"], **kwargs)
	raise RuntimeError("Unreachable")
