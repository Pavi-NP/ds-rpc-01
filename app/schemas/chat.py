# ds-rpc-01/app/schemas/chat.py
from typing import List, Dict, Any
from pydantic import BaseModel
from datetime import datetime


class SourceDocument(BaseModel):
    filename: str
    department: str
    summary: str
    relevance_score: float
    content_preview: str

class EnhancedChatResponse(BaseModel):
    response: str
    sources: List[SourceDocument] = []
    metadata: Dict[str, Any] = {}
    query_id: str
    timestamp: datetime
    processing_time_ms: int

class EnhancedChatRequest(BaseModel):
    message: str
    user_info: Dict[str, Any] = {}
    timestamp: datetime = datetime.now()
    # Add other fields as needed

class ChatRequest(BaseModel):
    """
    Defines the shape of a user's chat message request.
    """
    message: str

class ChatResponse(BaseModel):
    """
    Defines the shape of a response message.
    """
    reply: str
    
class UserInfo(BaseModel):
    username: str
    user_id: int
    role: str

class UserStats(BaseModel):
    user_id: int
    message_count: int
    last_active: str


class HealthCheck(BaseModel):
    status: str
    timestamp: datetime

class AdminUserInfo(BaseModel):
    user_id: int
    username: str
    email: str
    is_active: bool

class QueryOptions(BaseModel):
    """
    Defines options for querying the chat system.
    """
    query: str
    user_id: int
    role: str
    filters: Dict[str, Any] = {}
    sort_by: str = "relevance"
    limit: int = 10
    offset: int = 0
class QueryResponse(BaseModel):
    """
    Defines the shape of a response to a query.
    """
    results: List[Dict[str, Any]]
    total_count: int
    query_id: str
    processing_time_ms: int
    timestamp: datetime
    metadata: Dict[str, Any] = {}
class QueryError(BaseModel):
    """
    Defines the shape of an error response for a query.
    """
    error: str
    query_id: str
    timestamp: datetime
    details: Dict[str, Any] = {}
class QuerySuccess(BaseModel):
    """
    Defines the shape of a successful query response.
    """
    success: bool
    query_id: str
    timestamp: datetime
    message: str
    results: List[Dict[str, Any]] = []
    metadata: Dict[str, Any] = {}
class QueryStatus(BaseModel):
    """
    Defines the shape of a query status response.
    """
    query_id: str
    status: str
    timestamp: datetime
    message: str = ""
    results: List[Dict[str, Any]] = []
    metadata: Dict[str, Any] = {}

