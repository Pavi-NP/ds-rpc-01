# ds-rpc-01/app/main.py

import os
import logging
import uuid
import time
from datetime import datetime
import hashlib
import binascii


from datetime import datetime, timedelta
from typing import List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates
from jose import JWTError, jwt


from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from cachetools import TTLCache
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import custom schemas, services, and utilities
from app.schemas.chat import HealthCheck, EnhancedChatRequest, EnhancedChatResponse
from app.services.rag_service import rag_service

# ---------------------------
# Logging Configuration
# ---------------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ---------------------------
# Initialize Rate Limiter & Cache
# ---------------------------
limiter = Limiter(key_func=get_remote_address)
user_cache = TTLCache(maxsize=1000, ttl=300)  # 5 min cache for user info

# ---------------------------
# Security Configuration
# ---------------------------
SECRET_KEY = os.getenv("SECRET_KEY", "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
SALT_LENGTH = 16
HASH_ITERATIONS = 100000

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

# ---------------------------
# Password Hashing Functions
# ---------------------------
def hash_password(password: str) -> str:
    """Hash a password using PBKDF2_HMAC with SHA256"""
    salt = os.urandom(SALT_LENGTH)
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        HASH_ITERATIONS
    )
    return f"{binascii.hexlify(salt).decode()}:{binascii.hexlify(key).decode()}"

def verify_password(stored_password: str, provided_password: str) -> bool:
    """Verify a password against a stored hash"""
    try:
        salt_hex, stored_key_hex = stored_password.split(':')
        salt = binascii.unhexlify(salt_hex)
        
        new_key = hashlib.pbkdf2_hmac(
            'sha256',
            provided_password.encode('utf-8'),
            salt,
            HASH_ITERATIONS
        )
        # Convert both to hex for comparison
        return binascii.hexlify(new_key).decode() == stored_key_hex
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False

# ---------------------------
# User Database (Demo)
# ---------------------------
class User(BaseModel):
    username: str
    password_hash: str
    role: str
    title: str
    department: str
    
class SourceDoc(BaseModel):
    filename: str
    summary: Optional[str]

class EnhancedChatResponse(BaseModel):
    response: str
    sources: List[SourceDoc]

# Demo user database with hashed passwords
users_db = {
    "Peter": User(
        username="Peter",
        password_hash=hash_password("pete123"),
        role="engineering",
        title="Engineering Lead",
        department="Engineering"
    ),
    "Tony": User(
        username="Tony",
        password_hash=hash_password("password123"),
        role="engineering",
        title="Senior Engineer",
        department="Engineering"
    ),
    "Bruce": User(
        username="Bruce",
        password_hash=hash_password("securepass"),
        role="marketing",
        title="Marketing Director",
        department="Marketing"
    ),
    "Sam": User(
        username="Sam",
        password_hash=hash_password("financepass"),
        role="finance",
        title="Finance Manager",
        department="Finance"
    ),
    "Sid": User(
        username="Sid",
        password_hash=hash_password("sidpass123"),
        role="marketing",
        title="Marketing Specialist",
        department="Marketing"
    ),
    "Natasha": User(
        username="Natasha",
        password_hash=hash_password("hrpass123"),
        role="hr",
        title="HR Director",
        department="Human Resources"
    ),
    "Alex": User(
        username="Alex",
        password_hash=hash_password("ceopass"),
        role="c-level",
        title="Chief Executive Officer",
        department="Executive"
    ),
    "John": User(
        username="John",
        password_hash=hash_password("employeepass"),
        role="employee",
        title="General Employee",
        department="General"
    )
}

# ---------------------------
# Security Functions
# ---------------------------
def get_user(username: str):
    if username in users_db:
        return users_db[username]
    return None

def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(user.password_hash, password):
        logger.warning(f"Password verification failed for user {username}")
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = get_user(username)
    if user is None:
        raise credentials_exception
    return user

# ---------------------------
# Login Request Model
# ---------------------------
class LoginRequest(BaseModel):
    username: str
    password: str

# ---------------------------
# App Initialization
# ---------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting RAG-based RBAC Chatbot")
    try:
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        await rag_service.initialize(openai_api_key)
        logger.info("✅ RAG service initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize RAG service: {e}")
    yield
    logger.info("🛑 Shutting down application")
    await rag_service.cleanup()

# ---------------------------
# FastAPI app setup
# ---------------------------
app = FastAPI(
    title="Fintech RAG Assistant",
    description="RBAC chatbot with RAG-powered insights",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)

# ---------------------------
# Middleware Configuration
# ---------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.company.com"]
)

# Attach rate limiter exception handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ---------------------------
# API Endpoints
# ---------------------------

templates = Jinja2Templates(directory="templates")

@app.get("/", include_in_schema=False)
async def serve_index(request: Request):
    """Serve index.html with security headers."""
    response = templates.TemplateResponse("index.html", {"request": request})
    response.headers.update({
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains"
    })
    return response

@app.get("/api/health", response_model=HealthCheck)
async def health_check():
    """Check system health."""
    rag_healthy = await rag_service.health_check()
    return HealthCheck(status="healthy" if rag_healthy else "unhealthy")

@app.post("/api/login")
async def login_for_access_token(login_request: LoginRequest):
    """Authenticate user and return access token"""
    user = authenticate_user(login_request.username, login_request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    
    logger.info(f"User {user.username} logged in successfully")
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user.username,
        "role": user.role,
        "title": user.title,
        "department": user.department
    }

@app.post("/api/chat", response_model=EnhancedChatResponse)
@limiter.limit("30/minute")
async def enhanced_chat_endpoint(
    request: Request,
    chat_request: EnhancedChatRequest,
    user: User = Depends(get_current_user)
):
    """Process chat with RAG."""
    rag_response = await rag_service.query(
        question=chat_request.message,
        user_role=user.role,
        user_context={"username": user.username}
    )
    logger.info(f"User {user.username} queried: {chat_request.message}")
    return EnhancedChatResponse(
        response=rag_response["response"],
        sources=rag_response["sources"]
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(f"HTTP {exc.status_code}: {exc.detail} - {request.url}")
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

# ---------------------------
# Main: Run server
# ---------------------------
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
    
    
