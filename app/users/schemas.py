import enum

from pydantic import BaseModel as BaseSchema, EmailStr, Field, field_validator

from app.config import settings


class MembershipStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    BLOCKED = "BLOCKED"


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"


class UserRegisterRequest(BaseSchema):
    username: str
    email: EmailStr
    password: str = Field(
        min_length=settings.MIN_PASSWORD_LENGTH, max_length=settings.MAX_PASSWORD_LENGTH
    )

    @field_validator("password", mode="after")
    @classmethod
    def check_password(cls, password: str) -> str:
        from app.auth.utils import is_strong_password

        if not is_strong_password(password):
            raise ValueError(
                "Password must contain at least "
                "one lower character, "
                "one upper character, "
                "digit or special symbol"
            )

        return password


class User(UserRegisterRequest):
    role: UserRole = UserRole.USER


class UserResponse(BaseSchema):
    id: int
    username: str
    email: EmailStr

    class Config:
        from_attributes = True


class ChangeMembershipRequest(BaseSchema):
    user_id: int
    contact_information: str | None = None


class ChangeMembershipResponse(BaseSchema):
    user_id: int
    current_membership_status: MembershipStatus
