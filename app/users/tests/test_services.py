from typing import TYPE_CHECKING

from app.users.schemas import User
from app.users.services import UserService

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


async def test_create_user(session: "AsyncSession"):
    username = "test_user"
    email = "user@test.com"
    password = "test_password"
    result = await UserService.create_user(
        session, User(username=username, email=email, password=password)
    )
    assert result.username == username
    assert result.email == email
    assert result.password == password
