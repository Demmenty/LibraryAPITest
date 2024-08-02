import random
import re
import string
from datetime import datetime, timedelta

import bcrypt
from jose import jwt

from app.auth.models import RefreshTokenModel
from app.config import settings
from app.users.models import UserModel, UserRole

STRONG_PASSWORD_PATTERN = re.compile(
    r"^(?=.*[\d])(?=.*[A-Za-z])(?=.*[!@#%^&*])[A-Za-z\d!@#%^&*]{6,128}$"
)


def generate_random_alphanum(length: int = 20) -> str:
    """
    Generate a random alphanumeric string of a specified length.

    Args:
        length (int): The length of the generated string (default is 20).

    Returns:
        str: The randomly generated alphanumeric string.
    """

    alpha_num = string.ascii_letters + string.digits
    random_alphanum = "".join(random.choices(alpha_num, k=length))

    return random_alphanum


def get_refresh_token_cookie_settings(
    refresh_token: str,
    expired: bool = False,
) -> dict:
    """
    Get the settings for a refresh token cookie.

    Args:
        refresh_token (str): The refresh token value
        expired (bool, optional): Flag indicating if the token is expired. Defaults to False.

    Returns:
        dict: The settings for the refresh token cookie.
    """

    base_cookie = {
        "key": settings.REFRESH_TOKEN_KEY,
        "httponly": True,
        "samesite": "none",
        "secure": settings.SECURE_COOKIES,
        "domain": settings.SITE_DOMAIN,
    }
    if expired:
        return base_cookie

    return {
        **base_cookie,
        "value": refresh_token,
        "max_age": settings.REFRESH_TOKEN_EXP,
    }


def is_refresh_token_expired(refresh_token: RefreshTokenModel) -> bool:
    """
    Check if the refresh token has expired.

    Args:
        refresh_token (RefreshTokenModel): The refresh token database model.

    Returns:
        bool: True if the refresh token has expired, False otherwise.
    """

    return datetime.utcnow() > refresh_token.expires_at


def generate_access_token(
    user: UserModel,
    expires_delta: timedelta = timedelta(minutes=settings.JWT_EXP),
) -> str:
    """
    Generate an access token for the given user.

    Args:
        user (UserModel): The user for whom the access token is being generated.
        expires_delta (timedelta, optional): The expiration time for the token.
            Defaults to timedelta(minutes=settings.JWT_EXP).

    Returns:
        str: The generated access token.
    """

    jwt_data = {
        "sub": str(user.id),
        "exp": datetime.utcnow() + expires_delta,
        "is_admin": user.role == UserRole.ADMIN,
    }
    access_token = jwt.encode(jwt_data, settings.JWT_SECRET, algorithm=settings.JWT_ALG)

    return access_token


def hash_password(password: str) -> bytes:
    """
    Hashes the given password using bcrypt.

    Args:
        password (str): The password to be hashed.

    Returns:
        bytes: The hashed password.
    """

    pw = bytes(password, "utf-8")
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(pw, salt)

    return hashed_password


def check_password(password: str, password_in_db: bytes) -> bool:
    """
    Check if the provided password matches the password stored in the database.

    Args:
        password (str): The password to be checked.
        password_in_db (bytes): The hashed password stored in the database.

    Returns:
        bool: True if the password matches, False otherwise.
    """

    password_bytes = bytes(password, "utf-8")
    result = bcrypt.checkpw(password_bytes, password_in_db)

    return result


def is_strong_password(password: str) -> bool:
    """
    Check if the given password is a strong password.

    Args:
        password (str): The password to be checked.

    Returns:
        bool: True if the password is strong, False otherwise.
    """

    if re.match(STRONG_PASSWORD_PATTERN, password):
        return True

    return False
