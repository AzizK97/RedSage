from pydantic import BaseModel


class Conversation(BaseModel):
    id: str
    owner_user_id: str
    thread_id: str
    title: str