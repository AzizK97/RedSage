from pydantic import BaseModel

class Entitlement(BaseModel):
    user_id: str
    enabled: bool
    enabled_by_admin_id: str | None = None