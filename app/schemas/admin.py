from pydantic import BaseModel

class AdminUserInfo(BaseModel):
    user_id: int
    username: str
    email: str
    is_active: bool
    # add other relevant fields