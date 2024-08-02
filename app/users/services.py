from datetime import datetime

from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.auth.utils import check_password, hash_password
from app.books.services import BookService
from app.users import schemas
from app.users.exceptions import (
    ContactInformationNotProvided,
    UserIsNotLibraryMember,
    UserNotFound,
)
from app.users.models import LibraryMemberModel, UserModel

book_service = BookService()


class UserService:

    async def create_user(
        self,
        db: AsyncSession,
        user: schemas.User,
    ) -> UserModel:
        """
        Creates a new user in the database.

        Args:
            db (AsyncSession): The asynchronous database session.
            user (schemas.User): The user data to be created.

        Returns:
            UserModel: The created user.
        """

        new_user = UserModel(
            username=user.username,
            email=user.email,
            password=hash_password(user.password),
            created_at=datetime.utcnow(),
            role=user.role,
        )

        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        return new_user

    async def get_by_id(self, db: AsyncSession, user_id: int) -> UserModel | None:
        """
        Retrieves a user by their ID from the database.

        Args:
            db (AsyncSession): The asynchronous database session.
            user_id (int): The ID of the user to retrieve.

        Returns:
            UserModel | None: The user with the specified ID, or None if not found.
        """

        result = await db.execute(select(UserModel).filter(UserModel.id == user_id))
        user = result.scalars().first()

        return user

    async def get_by_username(self, db: AsyncSession, username: str) -> UserModel | None:
        """
        Retrieves a user by username from the database.

        Args:
            db (AsyncSession): The asynchronous database session.
            username (str): The username of the user to retrieve.

        Returns:
            UserModel | None: The user model if found, else None.
        """

        result = await db.execute(
            select(UserModel).filter(UserModel.username == username)
        )
        user = result.scalars().first()

        return user

    async def get_by_email(self, db: AsyncSession, email: str) -> UserModel | None:
        """
        Retrieves a user by email from the database.

        Args:
            db (AsyncSession): The asynchronous database session.
            email (str): The email of the user to retrieve.

        Returns:
            UserModel | None: The user model if found, else None.
        """

        result = await db.execute(select(UserModel).filter(UserModel.email == email))
        user = result.scalars().first()

        return user

    async def authenticate(
        self,
        db: AsyncSession,
        form_data: OAuth2PasswordRequestForm,
    ) -> UserModel | None:
        """
        Asynchronously authenticate a user using the provided OAuth2PasswordRequestForm.

        Args:
            db (AsyncSession): The asynchronous database session.
            form_data (OAuth2PasswordRequestForm): The OAuth2PasswordRequestForm to authenticate.

        Returns:
            UserModel | None: The authenticated user, or None if authentication fails.
        """

        user = await self.get_by_username(db, form_data.username)

        if not user or not check_password(form_data.password, user.password):
            return None

        return user

    async def activate_membership(
        self,
        db: AsyncSession,
        user_id: int,
        contact_information: str | None = None,
    ):
        """
        Activate a user's library membership.

        Args:
            db: An AsyncSession representing the database session.
            user_id: An integer representing the user's ID.
            contact_information: A string representing the user's contact information, default is None.
        """

        user = await self.get_by_id(db, user_id)
        if not user:
            raise UserNotFound()

        user_membership = user.library_member

        if not user_membership:
            if not contact_information:
                raise ContactInformationNotProvided()

            user.library_member = LibraryMemberModel(
                id=user_id,
                contact_information=contact_information,
                membership_status=schemas.MembershipStatus.ACTIVE,
            )
            await db.commit()
            return

        if user_membership:
            if user_membership.membership_status == schemas.MembershipStatus.BLOCKED:
                user.library_member.membership_status = schemas.MembershipStatus.ACTIVE
                await db.commit()
                return

    async def block_membership(
        self,
        db: AsyncSession,
        user_id: int,
    ):
        """
        Blocks a user's library membership.

        Args:
            db (AsyncSession): The asynchronous database session.
            user_id (int): The ID of the user whose membership is to be blocked.
        """

        user = await self.get_by_id(db, user_id)
        if not user:
            raise UserNotFound()

        user_membership = user.library_member

        if not user_membership:
            raise UserIsNotLibraryMember()

        if user_membership.membership_status == schemas.MembershipStatus.ACTIVE:
            user.library_member.membership_status = schemas.MembershipStatus.BLOCKED
            await db.commit()
            return

    async def add_unavailable_categories(
        self,
        db: AsyncSession,
        user_id: int,
        categories_id: list[int],
    ) -> UserModel:
        """
        Adds unavailable book categories for a user in the database.

        Args:
            db (AsyncSession): The async database session.
            user_id (int): The ID of the user.
            categories_id (list[int]): The IDs of the categories to be marked as unavailable for the user.

        Returns:
            UserModel: The updated user object after adding the unavailable categories.
        """

        user = await self.get_by_id(db, user_id)
        if not user:
            raise UserNotFound()

        for category_id in categories_id:
            category = await book_service.get_category_by_id(db, category_id)
            if category:
                user.unavailable_book_categories.append(category)

        await db.commit()
        await db.refresh(user)

        return user

    async def remove_unavailable_categories(
        self,
        db: AsyncSession,
        user_id: int,
        categories_id: list[int],
    ) -> UserModel:
        """
        Removes unavailable book categories for a user in the database.

        Args:
            db (AsyncSession): The async database session.
            user_id (int): The ID of the user.
            categories_id (list[int]): The IDs of the categories to be removed from the unavailable list.

        Returns:
            UserModel: The updated user object after removing the categories.
        """

        user = await self.get_by_id(db, user_id)
        if not user:
            raise UserNotFound()

        for category_id in categories_id:
            category = await book_service.get_category_by_id(db, category_id)
            if category and category in user.unavailable_book_categories:
                user.unavailable_book_categories.remove(category)

        await db.commit()
        await db.refresh(user)

        return user
