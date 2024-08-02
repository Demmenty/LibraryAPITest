from fastapi import APIRouter, Cookie, Depends, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_user_from_refresh_token
from app.auth.exceptions import InvalidCredentials
from app.auth.schemas import (
    AccessTokenResponse,
    SuccessLoginPesponse,
    SuccessLogoutPesponse,
)
from app.auth.services import TokenService
from app.auth.utils import generate_access_token, get_refresh_token_cookie_settings
from app.database import get_db
from app.users.exceptions import EmailTaken, UsernameTaken
from app.users.schemas import User, UserRegisterRequest, UserResponse, UserRole
from app.users.services import UserService

router = APIRouter()


@router.post(
    "/register", status_code=status.HTTP_201_CREATED, response_model=UserResponse
)
async def register(
    new_user: UserRegisterRequest,
    db: AsyncSession = Depends(get_db),
    user_service: UserService = Depends(UserService),
) -> dict:
    """Register a new user with the provided authentication data"""

    if await user_service.get_by_email(db, new_user.email):
        raise EmailTaken()

    if await user_service.get_by_username(db, new_user.username):
        raise UsernameTaken()

    new_user = User(**new_user.model_dump())
    new_user.role = UserRole.USER

    user = await user_service.create_user(db, new_user)

    return user


@router.post("/login", response_model=SuccessLoginPesponse)
async def login(
    response: Response,
    db: AsyncSession = Depends(get_db),
    auth_form: OAuth2PasswordRequestForm = Depends(),
    token_service: TokenService = Depends(TokenService),
    user_service: UserService = Depends(UserService),
) -> dict:
    """Authenticates user and sets a cookie with the refresh token"""

    user = await user_service.authenticate(db, auth_form)
    if not user:
        raise InvalidCredentials()

    refresh_token_value = await token_service.create_refresh_token(db, user_id=user.id)
    refresh_token_settings = get_refresh_token_cookie_settings(refresh_token_value)
    response.set_cookie(**refresh_token_settings)

    return SuccessLoginPesponse()


@router.post("/token", response_model=AccessTokenResponse)
async def get_api_access_token(
    user: User = Depends(get_user_from_refresh_token),
) -> dict:
    """Generates a new API access token for logged user"""

    access_token = generate_access_token(user=user)

    return AccessTokenResponse(access_token=access_token)


@router.post("/logout", response_model=SuccessLogoutPesponse)
async def logout_user(
    response: Response,
    db: AsyncSession = Depends(get_db),
    refresh_token_value: str = Cookie(..., alias="refreshToken"),
    token_service: TokenService = Depends(TokenService),
) -> None:
    """Deletes the refresh token from cookie and expires it"""

    if not refresh_token_value:
        return SuccessLogoutPesponse()

    refresh_token = await token_service.get_refresh_token_by_value(
        db, refresh_token_value
    )
    if refresh_token:
        await token_service.expire_refresh_token(db, refresh_token.uuid)

    refresh_token_settings = get_refresh_token_cookie_settings(
        refresh_token_value, expired=True
    )
    response.delete_cookie(**refresh_token_settings)

    return SuccessLogoutPesponse()
