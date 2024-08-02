from app.exceptions import BadRequest, NotFound


class ErrorCode:
    EMAIL_TAKEN = "Email is already taken."
    USERNAME_TAKEN = "Username is already taken."
    USER_NOT_FOUND = "User not found."
    USER_NOT_LIBRARY_MEMBER = "User is not a library member."
    CONTACT_INFORMATION_NOT_PROVIDED = (
        "Contact information must be provided for a new library member."
    )


class EmailTaken(BadRequest):
    DETAIL = ErrorCode.EMAIL_TAKEN


class UsernameTaken(BadRequest):
    DETAIL = ErrorCode.USERNAME_TAKEN


class UserNotFound(NotFound):
    DETAIL = ErrorCode.USER_NOT_FOUND


class UserIsNotLibraryMember(BadRequest):
    DETAIL = ErrorCode.USER_NOT_LIBRARY_MEMBER


class ContactInformationNotProvided(BadRequest):
    DETAIL = ErrorCode.CONTACT_INFORMATION_NOT_PROVIDED
