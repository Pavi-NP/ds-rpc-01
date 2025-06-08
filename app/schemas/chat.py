# ds-rpc-01/app/schemas/chat.py

from pydantic import BaseModel

class ChatRequest(BaseModel):
    """
    Defines the shape of a user's chat message request.
    """
    message: str
