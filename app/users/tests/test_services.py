from datetime import datetime
from typing import TYPE_CHECKING

import pytest
from pytz import utc

from app.auth.utils import check_password
from app.users.models import UserModel
from app.users.schemas import User, UserRole
from app.users.services import UserService

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_create_user_success(session: "AsyncSession", user_service: UserService):
    username = "test_user"
    email = "user@test.com"
    password = "Test_password1!"
    role = UserRole.USER

    user_input = User(username=username, email=email, password=password, role=role)
    created_user = await user_service.create_user(session, user_input)

    assert created_user.username == username
    assert created_user.email == email
    assert created_user.role == role
    assert created_user.password != password
    assert check_password(password, created_user.password)

    user_from_db = await session.get(UserModel, created_user.id)

    assert user_from_db is not None
    assert user_from_db.username == username
    assert user_from_db.email == email
    assert user_from_db.role == role
    assert user_from_db.password != password
    assert check_password(password, user_from_db.password)
    assert user_from_db.created_at <= datetime.now(utc)
