from pydantic import BaseModel as BaseSchema, Field


class JWTData(BaseSchema):
    user_id: int = Field(alias="sub")
    is_admin: bool = False


class AccessTokenResponse(BaseSchema):
    access_token: str
    detail: str | None = (
        "Use the access_token in the 'Authorization' header "
        "in the format 'Bearer <token>' to access the API functions"
    )


class SuccessLoginPesponse(BaseSchema):
    detail: str = "Login successful"


class SuccessLogoutPesponse(BaseSchema):
    detail: str = "Logout successful"
