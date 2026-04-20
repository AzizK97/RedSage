from pydantic import BaseModel


class MeResponse(BaseModel):
    id: str
    redmine_user_id: int
    role: str
    enabled: bool