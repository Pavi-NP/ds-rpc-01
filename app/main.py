# ds-rpc-01/app/main.py

from typing import Dict
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.schemas.chat import ChatRequest
from app.services.rag_service import rag_service
from app.utils.rbac import get_accessible_files

app = FastAPI(
    title="Fintech RAG Assistant",
    description="A role-based chatbot for accessing departmental insights.",
    version="1.0.0"
)
security = HTTPBasic()

# --- Static File and Template Configuration ---
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# --- User Database & Authentication ---
# In a real app, this would be a proper database.
users_db: Dict[str, Dict[str, str]] = {
    "Peter": {"password": "pete123", "role": "engineering"},
    "Tony": {"password": "password123", "role": "engineering"},
    "Bruce": {"password": "securepass", "role": "marketing"},
    "Sam": {"password": "financepass", "role": "finance"},
    "Sid": {"password": "sidpass123", "role": "marketing"},
    "Natasha": {"password": "hrpass123", "role": "hr"},
    "Alex": {"password": "ceopass", "role": "c-level"},
    "John": {"password": "employeepass", "role": "employee"},
}

def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    """Dependency to authenticate and retrieve the current user."""
    username = credentials.username
    password = credentials.password
    user = users_db.get(username)
    
    if not user or user["password"] != password:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return {"username": username, "role": user["role"]}

# --- API Endpoints ---

@app.get("/", include_in_schema=False)
async def serve_index(request: Request):
    """Serves the main index.html file."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/user-info")
def get_user_info(user: dict = Depends(get_current_user)):
    """Provides user info to the frontend after successful authentication."""
    return {"username": user['username'], "role": user['role']}

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest, user: dict = Depends(get_current_user)):
    """
    Processes a user's query using the RAG service based on their role.
    """
    user_role = user["role"]
    accessible_files = get_accessible_files(user_role)
    
    response_text = rag_service.query(request.message, accessible_files)
    
    return {"response": response_text}
