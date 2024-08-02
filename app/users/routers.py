from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import (
    get_admin_from_refresh_token,
    get_user_from_refresh_token,
)
from app.database import get_db
from app.users.exceptions import EmailTaken, UsernameTaken
from app.users.models import UserModel
from app.users.schemas import (
    ChangeMembershipRequest,
    ChangeMembershipResponse,
    MembershipStatus,
    User,
    UserResponse,
)
from app.users.services import UserService

router = APIRouter()


@router.post("/create", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def create_user(
    new_user: User,
    db: AsyncSession = Depends(get_db),
    user_service: UserService = Depends(UserService),
    admin: UserModel = Depends(get_admin_from_refresh_token),
) -> dict:
    """
    Only for admins.
    Create a new user with the provided credentials and role.
    """

    if await user_service.get_by_email(db, new_user.email):
        raise EmailTaken()

    if await user_service.get_by_username(db, new_user.username):
        raise UsernameTaken()

    user = await user_service.create_user(db, new_user)

    return user


@router.get("/me", response_model=UserResponse)
async def get_me(user: UserModel = Depends(get_user_from_refresh_token)) -> dict:
    """Get the logged user information"""

    return user


@router.post("/membership/activate", response_model=ChangeMembershipResponse)
async def activate_membership(
    data: ChangeMembershipRequest,
    db: AsyncSession = Depends(get_db),
    user_service: UserService = Depends(UserService),
    admin: UserModel = Depends(get_admin_from_refresh_token),
) -> dict:
    """
    Only for admins.
    Activate library membership of a certain user.
    """

    await user_service.activate_membership(db, data.user_id, data.contact_information)

    return ChangeMembershipResponse(
        user_id=data.user_id, current_membership_status=MembershipStatus.ACTIVE
    )


@router.post("/membership/block", response_model=ChangeMembershipResponse)
async def block_membership(
    data: ChangeMembershipRequest,
    db: AsyncSession = Depends(get_db),
    user_service: UserService = Depends(UserService),
    admin: UserModel = Depends(get_admin_from_refresh_token),
) -> dict:
    """
    Only for admins.
    Blocks library membership of a certain user.
    """

    await user_service.block_membership(db, data.user_id)

    return ChangeMembershipResponse(
        user_id=data.user_id, current_membership_status=MembershipStatus.BLOCKED
    )
