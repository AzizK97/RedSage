from pydantic import BaseModel, EmailStr

class RedmineUser(BaseModel):
    id: int
    redmine_user_id: int
    email: EmailStr
    full_name: str
    role: str