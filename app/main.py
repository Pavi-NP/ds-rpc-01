# ds-rpc-01/app/main.py

import os
import logging
from datetime import datetime
from typing import Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates

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
from app.utils.security import SecurityManager

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
# Security & App Initialization
# ---------------------------
security_manager = SecurityManager()
security = HTTPBasic()

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
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
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
# Authentication: Get Current User
# ---------------------------
async def get_current_user(credentials: HTTPBasicCredentials = Depends(security)) -> Dict[str, Any]:
    username = credentials.username
    password = credentials.password
    
    cache_key = f"user:{username}"
    if cache_key in user_cache:
        cached_user = user_cache[cache_key]
        if security_manager.verify_password(password, cached_user["password_hash"]):
            return cached_user

    user = users_db.get(username)
    if not user or not security_manager.verify_password(password, user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    user["last_login"] = datetime.utcnow()
    user_cache[cache_key] = user
    return user

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

@app.post("/api/chat", response_model=EnhancedChatResponse)
@limiter.limit("30/minute")
async def enhanced_chat_endpoint(
    request: Request,
    chat_request: EnhancedChatRequest,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """Process chat with RAG."""
    rag_response = await rag_service.query(
        question=chat_request.message,
        user_role=user["role"],
        user_context={"username": user["username"]}
    )
    print(f"User {user['username']} queried: {rag_response['response']}")
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
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)



# import os
# import logging
# from datetime import datetime
# from typing import Dict, Any, List
# from contextlib import asynccontextmanager

# from fastapi import FastAPI, HTTPException, Depends, Request, status, APIRouter
# from fastapi.security import HTTPBasic, HTTPBasicCredentials
# from fastapi.staticfiles import StaticFiles
# from fastapi.templating import Jinja2Templates
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.middleware.trustedhost import TrustedHostMiddleware
# from fastapi.responses import JSONResponse
# from pydantic import BaseModel

# from slowapi import Limiter, _rate_limit_exceeded_handler
# from slowapi.util import get_remote_address
# from slowapi.errors import RateLimitExceeded

# from cachetools import TTLCache
# import uvicorn
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()

# # Import custom schemas, services, and utilities
# from app.schemas.chat import UserInfo, HealthCheck, EnhancedChatRequest, EnhancedChatResponse
# from app.services.rag_service import rag_service
# from app.utils.audit import audit_logger
# from app.utils.security import SecurityManager

# # ---------------------------
# # Logging Configuration
# # ---------------------------
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
# )
# logger = logging.getLogger(__name__)

# # ---------------------------
# # Initialize Rate Limiter & Cache
# # ---------------------------
# limiter = Limiter(key_func=get_remote_address)
# user_cache = TTLCache(maxsize=1000, ttl=300)  # 5 min cache for user info

# # ---------------------------
# # Security & App Initialization
# # ---------------------------
# security_manager = SecurityManager()
# security = HTTPBasic()

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     logger.info("🚀 Starting RAG-based RBAC Chatbot")
#     try:
#         openai_api_key = os.getenv("OPENAI_API_KEY")
#         if not openai_api_key:
#             raise ValueError("OPENAI_API_KEY not found in environment variables")
#         await rag_service.initialize(
#             openai_api_key,
#             persist_directory='./vector_store'
#         )
#         logger.info("✅ RAG service initialized successfully")
#     except Exception as e:
#         logger.error(f"❌ Failed to initialize RAG service: {e}")
#     yield
#     logger.info("🛑 Shutting down application")
#     await rag_service.cleanup()


# # @asynccontextmanager
# # async def lifespan(app: FastAPI):
# #     logger.info("🚀 Starting RAG-based RBAC Chatbot")
# #     try:
# #         openai_api_key = os.getenv("OPENAI_API_KEY")
# #         if not openai_api_key:
# #             raise ValueError("OPENAI_API_KEY not found in environment variables")
# #         await rag_service.initialize(
# #             openai_api_key,
# #             persist_directory='./vector_store'
# #         )
# #         logger.info("✅ RAG service initialized successfully")
# #     except Exception as e:
# #         logger.error(f"❌ Failed to initialize RAG service: {e}")
# #     yield
# #     logger.info("🛑 Shutting down application")
# #     await rag_service.cleanup()

# # ---------------------------
# # FastAPI app setup
# # ---------------------------
# app = FastAPI(
#     title="Fintech RAG Assistant",
#     description="RBAC chatbot with RAG-powered insights",
#     version="2.0.0",
#     docs_url="/api/docs",
#     redoc_url="/api/redoc",
#     lifespan=lifespan,
# )

# # ---------------------------
# # Middleware Configuration
# # ---------------------------
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:3000", "http://localhost:8000"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# app.add_middleware(
#     TrustedHostMiddleware,
#     allowed_hosts=["localhost", "127.0.0.1", "*.company.com"]
# )

# # Attach rate limiter exception handler
# app.state.limiter = limiter
# app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# # ---------------------------
# # Static files & Templates
# # ---------------------------
# app.mount("/static", StaticFiles(directory="static"), name="static")
# templates = Jinja2Templates(directory="templates")

# # ---------------------------
# # Authentication: Get Current User
# # ---------------------------
# async def get_current_user(credentials: HTTPBasicCredentials = Depends(security)) -> Dict[str, Any]:
#     username = credentials.username
#     password = credentials.password
#     # Check cache first
#     cache_key = f"user:{username}"
#     if cache_key in user_cache:
#         cached_user = user_cache[cache_key]
#         if security_manager.verify_password(password, cached_user["password_hash"]):
#             return cached_user
    
#     # Validate against db
#     user = users_db.get(username)
#     if not user or not security_manager.verify_password(password, user["password_hash"]):
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
#     # Update last login and cache user info
#     user["last_login"] = datetime.utcnow()
#     user_cache[cache_key] = user
#     return user

# # ---------------------------
# # API Endpoints
# # ---------------------------

# @app.get("/", include_in_schema=False)
# async def serve_index(request: Request):
#     """Serve index.html with security headers."""
#     response = templates.TemplateResponse("index.html", {"request": request})
#     response.headers.update({
#         "X-Content-Type-Options": "nosniff",
#         "X-Frame-Options": "DENY",
#         "X-XSS-Protection": "1; mode=block",
#         "Strict-Transport-Security": "max-age=31536000; includeSubDomains"
#     })
#     return response


# @app.get("/api/health", response_model=HealthCheck)
# async def health_check():
#     """Check system health."""
#     rag_healthy = await rag_service.health_check()
#     return HealthCheck(status="healthy" if rag_healthy else "unhealthy")

# @app.post("/api/chat", response_model=EnhancedChatResponse)
# @limiter.limit("30/minute")
# async def enhanced_chat_endpoint(
#     request: Request,
#     chat_request: EnhancedChatRequest,
#     user: Dict[str, Any] = Depends(get_current_user)
# ):
#     """Process chat with RAG."""
#     rag_response = await rag_service.query(
#         question=chat_request.message,
#         user_role=user["role"],
#         user_context={"username": user["username"]}
#     )
#     # return EnhancedChatResponse(
#     #     response=rag_response["response"], 
#     #     sources=rag_response["sources"])
    
#     # Print inside the function, where `user` is available
#     print(f"User {user['username']} queried: {rag_response['response']}")
#     return EnhancedChatResponse(
#         response=rag_response["response"],
#         sources=rag_response["sources"]
#     )

# # ---------------------------
# # Error Handlers
# # ---------------------------
# @app.exception_handler(HTTPException)
# async def http_exception_handler(request: Request, exc: HTTPException):
#     logger.warning(f"HTTP {exc.status_code}: {exc.detail} - {request.url}")
#     return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

# # ---------------------------
# # Main: Run server
# # ---------------------------
# if __name__ == "__main__":
#     uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    
    