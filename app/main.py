from typing import Dict

from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials

#FastAPI's CORSMiddleware allows your backend API to specify which origins are permitted to access its resources. 
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Fintech RAG Assistant",
    description="A Retrieval-Augmented Generation Assistant for business insights using internal documents.",
    version="1.0.0"
)

# Enable CORS for all origins (adjust in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with frontend URL(s) in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Simulated user database
users_db: Dict[str, Dict[str, str]] = {
    "Tony": {"password": "password123", "role": "engineering"},
    "Bruce": {"password": "securepass", "role": "marketing"},
    "Sam": {"password": "financepass", "role": "finance"},
    "Peter": {"password": "pete123", "role": "engineering"},
    "Sid": {"password": "sidpass123", "role": "marketing"},
    "Natasha": {"password": "hrpass123", "role": "hr"}
}
security = HTTPBasic()

# Dependency: Authenticate user
def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    username = credentials.username
    password = credentials.password
    user = users_db.get(username)
    if not user or user["password"] != password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"username": username, "role": user["role"]}

# Endpoint: Verify login
@app.get("/login")
def login(user=Depends(get_current_user)):
    return {
        "message": f"Welcome {user['username']}!",
        "role": user["role"]
    }

# Endpoint: RAG query using user's role
@app.post("/query", response_model=QueryResponse)
def query_rag(request: QueryRequest, current_user=Depends(get_current_user)):
    """
    Query the RAG pipeline with a question.
    User authentication is required.
    """
    result = get_insight(request.query, current_user["role"])
    return QueryResponse(
        answer=result["answer"],
        source_documents=result["source_documents"]
    )

# Endpoint: Test authenticated access
@app.get("/test")
def test(user=Depends(get_current_user)):
    return {
        "message": f"Hello {user['username']}! Your role is {user['role']}.",
        "role": user["role"]
    }
