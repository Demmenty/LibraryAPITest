import uuid
from datetime import datetime, timedelta

from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.auth import utils as auth_utils
from app.auth.models import RefreshTokenModel
from app.config import settings


class TokenService:

    async def create_refresh_token(
        self,
        db: AsyncSession,
        user_id: int,
    ) -> str:
        """
        Creates new refresh token for a user and saves it in the database.

        Args:
            db (AsyncSession): The asynchronous database session.
            user_id (int): The ID of the user for whom the refresh token is being created.

        Returns:
            str: The generated refresh token value.
        """

        refresh_token_value = auth_utils.generate_random_alphanum(64)

        new_token = RefreshTokenModel(
            user_id=user_id,
            refresh_token=refresh_token_value,
            expires_at=datetime.utcnow() + timedelta(seconds=settings.REFRESH_TOKEN_EXP),
            uuid=str(uuid.uuid4()),
        )

        db.add(new_token)
        await db.commit()

        return refresh_token_value

    async def get_refresh_token_by_value(
        self,
        db: AsyncSession,
        refresh_token: str,
    ) -> RefreshTokenModel | None:
        """
        Asynchronous function to retrieve a refresh token from the database.

        Args:
            db (AsyncSession): The asynchronous session to interact with the database.
            refresh_token (str): The refresh token to retrieve.

        Returns:
            Union[RefreshTokenModel, None]: The retrieved refresh token, if found, or None.
        """

        q = select(RefreshTokenModel).filter(
            RefreshTokenModel.refresh_token == refresh_token
        )
        result = await db.execute(q)

        return result.scalars().first()

    async def get_refresh_token_by_uuid(
        self, db: AsyncSession, refresh_token_uuid: str
    ) -> RefreshTokenModel | None:
        """
        Retrieves a refresh token by its UUID from the database.

        Args:
            db: An AsyncSession representing the database session.
            refresh_token_uuid: A string representing the UUID of the refresh token.

        Returns:
            Union[RefreshTokenModel, None]: The retrieved refresh token, if found, or None.
        """

        q = select(RefreshTokenModel).filter(
            RefreshTokenModel.uuid == refresh_token_uuid
        )
        result = await db.execute(q)
        token = result.scalars().first()

        return token

    async def expire_refresh_token(
        self, db: AsyncSession, refresh_token_uuid: UUID4
    ) -> None:
        """
        Expire the refresh token for the given refresh token UUID.

        Args:
            db (AsyncSession): The database session.
            refresh_token_uuid: The UUID of the refresh token to expire.
        """

        token = await self.get_refresh_token_by_uuid(db, refresh_token_uuid)

        if token:
            token.expires_at = datetime.utcnow() - timedelta(days=1)
            await db.commit()
