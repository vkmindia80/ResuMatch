from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from motor.motor_asyncio import AsyncIOMotorClient
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database instance
db_client = None
db = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global db_client, db
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017/resumatch')
    db_client = AsyncIOMotorClient(mongo_url)
    db = db_client.get_database()
    
    # Create indexes
    await db.users.create_index("email", unique=True)
    await db.users.create_index("created_at")
    await db.profiles.create_index("user_id", unique=True)
    await db.job_descriptions.create_index("user_id")
    await db.resumes.create_index("user_id")
    await db.interview_questions.create_index("user_id")
    
    print("✅ Connected to MongoDB")
    print(f"✅ Database: {db.name}")
    
    yield
    
    # Shutdown
    db_client.close()
    print("❌ Disconnected from MongoDB")

app = FastAPI(
    title="ResuMatch AI API",
    description="AI-powered resume optimization and interview preparation platform",
    version="1.0.0",
    lifespan=lifespan
)

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
async def root():
    return {
        "message": "Welcome to ResuMatch AI API",
        "version": "1.0.0",
        "status": "active"
    }

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "connected" if db_client else "disconnected"
    }

# Dependency to get database
def get_database():
    return db
