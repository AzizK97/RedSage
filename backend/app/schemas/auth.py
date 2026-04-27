from pydantic import BaseModel


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    full_name: str
    token_type: str = "bearer"


class MeResponse(BaseModel):
    id: str
    redmine_user_id: int
    role: str
    enabled: bool