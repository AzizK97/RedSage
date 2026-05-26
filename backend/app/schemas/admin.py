from pydantic import BaseModel


class SetPmAccessRequest(BaseModel):
    redmine_user_id: int
    enabled: bool


class PmCandidate(BaseModel):
    redmine_user_id: int
    email: str
    full_name: str
    in_platform: bool
    enabled: bool
    projects_name: list[str]