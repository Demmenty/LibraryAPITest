from fastapi import status

from app.exceptions import DetailedHTTPException


class ErrorCode:
    AUTHENTICATION_REQUIRED = "Authentication required."
    AUTHORIZATION_FAILED = "Authorization failed. User has no access."
    INVALID_TOKEN = "Invalid token."
    INVALID_CREDENTIALS = "Invalid credentials."
    REFRESH_TOKEN_NOT_VALID = "Refresh token is not valid."
    REFRESH_TOKEN_REQUIRED = "Refresh token is required either in the body or cookie."
    ACCESS_TOKEN_REQUIRED = "Access token is required in the Authorization header."
    ACCESS_TOKEN_EXPIRED = "Access token has expired. Get a new one."


class NotAuthenticated(DetailedHTTPException):
    STATUS_CODE = status.HTTP_401_UNAUTHORIZED
    DETAIL = "User not authenticated"

    def __init__(self) -> None:
        super().__init__(headers={"WWW-Authenticate": "Bearer"})


class PermissionDenied(DetailedHTTPException):
    STATUS_CODE = status.HTTP_403_FORBIDDEN
    DETAIL = "Permission denied"


class AuthRequired(NotAuthenticated):
    DETAIL = ErrorCode.AUTHENTICATION_REQUIRED


class AuthorizationFailed(PermissionDenied):
    DETAIL = ErrorCode.AUTHORIZATION_FAILED


class InvalidCredentials(NotAuthenticated):
    DETAIL = ErrorCode.INVALID_CREDENTIALS


class RefreshTokenNotValid(NotAuthenticated):
    DETAIL = ErrorCode.REFRESH_TOKEN_NOT_VALID


class AccessTokenRequired(PermissionDenied):
    DETAIL = ErrorCode.ACCESS_TOKEN_REQUIRED


class AccessTokenExpired(PermissionDenied):
    DETAIL = ErrorCode.ACCESS_TOKEN_EXPIRED


class AccessTokenInvalid(PermissionDenied):
    DETAIL = ErrorCode.INVALID_TOKEN
