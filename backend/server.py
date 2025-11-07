from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
from database import connect_to_mongo, close_mongo_connection, get_database
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

# Import middleware and logging
from middleware.rate_limit import limiter
from middleware.security import (
    add_security_headers,
    request_logging_middleware,
    validate_content_length
)
from utils.logging_config import app_logger, log_info

# Load environment variables
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    log_info("Starting ResuMatch AI API server...")
    await connect_to_mongo()
    log_info("ResuMatch AI API server started successfully")
    yield
    # Shutdown
    log_info("Shutting down ResuMatch AI API server...")
    await close_mongo_connection()
    log_info("ResuMatch AI API server shutdown complete")

app = FastAPI(
    title="ResuMatch AI API",
    description="AI-powered resume optimization and interview preparation platform",
    version="1.0.0",
    lifespan=lifespan
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add security middleware (order matters!)
app.middleware("http")(validate_content_length)
app.middleware("http")(request_logging_middleware)
app.middleware("http")(add_security_headers)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Import routers
from routers import auth, users, profiles, jobs, resumes, interviews

# Register routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(profiles.router, prefix="/api/profiles", tags=["Profiles"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["Job Descriptions"])
app.include_router(resumes.router, prefix="/api/resumes", tags=["Resumes"])
app.include_router(interviews.router, prefix="/api/interviews", tags=["Interview Prep"])

@app.get("/")
@limiter.limit("20/minute")
async def root(request: Request):
    return {
        "message": "Welcome to ResuMatch AI API",
        "version": "1.0.0",
        "status": "active"
    }

@app.get("/api/health")
@limiter.limit("60/minute")
async def health_check(request: Request):
    db = get_database()
    return {
        "status": "healthy",
        "database": "connected" if db is not None else "disconnected",
        "version": "1.0.0"
    }
