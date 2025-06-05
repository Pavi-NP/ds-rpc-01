from pydantic import BaseModel
from typing import List, Optional

class QueryRequest(BaseModel):
    query: str
    role: str

class QueryResponse(BaseModel):
    answer: str
    source_documents: Optional[List[str]] = None
