import pytest
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from httpx import AsyncClient, ASGITransport
import uuid
from datetime import datetime
import os

# Set test environment
os.environ["TESTING"] = "1"

from server import app
from database import get_database
from utils.auth import get_password_hash, create_access_token

# Test database configuration
TEST_MONGO_URL = os.getenv("TEST_MONGO_URL", "mongodb://localhost:27017/resumatch_test")


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_db():
    """Create test database connection"""
    client = AsyncIOMotorClient(TEST_MONGO_URL)
    db = client.get_database()
    
    # Create indexes
    await db.users.create_index("email", unique=True)
    await db.profiles.create_index("user_id", unique=True)
    
    yield db
    
    # Cleanup: Drop test database
    await client.drop_database(db.name)
    client.close()


@pytest.fixture(autouse=True)
async def clean_db(test_db):
    """Clean database before each test"""
    # Clean all collections
    await test_db.users.delete_many({})
    await test_db.profiles.delete_many({})
    await test_db.job_descriptions.delete_many({})
    await test_db.resumes.delete_many({})
    await test_db.interview_questions.delete_many({})
    yield


@pytest.fixture
async def client(test_db):
    """Create test client"""
    # Override database dependency
    app.dependency_overrides[get_database] = lambda: test_db
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
async def test_user(test_db):
    """Create a test user"""
    user_id = str(uuid.uuid4())
    user_data = {
        "id": user_id,
        "email": "test@example.com",
        "full_name": "Test User",
        "password_hash": get_password_hash("testpass123"),
        "is_verified": True,
        "subscription_tier": "free",
        "google_id": None,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "last_login": None
    }
    await test_db.users.insert_one(user_data)
    return user_data


@pytest.fixture
async def auth_token(test_user):
    """Create authentication token for test user"""
    return create_access_token(data={"sub": test_user["id"]})


@pytest.fixture
async def auth_headers(auth_token):
    """Create authentication headers"""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
async def test_profile(test_db, test_user):
    """Create a test profile"""
    profile_data = {
        "id": str(uuid.uuid4()),
        "user_id": test_user["id"],
        "personal_info": {
            "full_name": "Test User",
            "email": "test@example.com",
            "phone": "+1234567890",
            "location": "San Francisco, CA",
            "title": "Software Engineer",
        },
        "education": [
            {
                "institution": "Test University",
                "degree": "Bachelor of Science",
                "field": "Computer Science",
                "start_date": "2015-09-01",
                "end_date": "2019-05-01",
                "gpa": 3.8
            }
        ],
        "experience": [
            {
                "company": "Tech Corp",
                "title": "Software Engineer",
                "employment_type": "Full-time",
                "start_date": "2019-06-01",
                "end_date": None,
                "is_current": True,
                "location": "San Francisco, CA",
                "responsibilities": ["Develop features", "Write tests"],
                "achievements": ["Improved performance by 50%"],
                "technologies": ["Python", "React"]
            }
        ],
        "skills": {
            "technical": [{"name": "Python", "level": "Expert"}],
            "soft": ["Communication", "Leadership"],
            "languages": [{"name": "English", "fluency": "Native"}],
            "tools": ["Git", "Docker"]
        },
        "projects": [],
        "certifications": [],
        "completeness_score": 75,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    await test_db.profiles.insert_one(profile_data)
    return profile_data


@pytest.fixture
async def test_job(test_db, test_user):
    """Create a test job description"""
    job_data = {
        "id": str(uuid.uuid4()),
        "user_id": test_user["id"],
        "title": "Senior Software Engineer",
        "company": "Tech Corp",
        "location": "San Francisco, CA",
        "job_type": "Full-time",
        "description": "Looking for a senior software engineer with Python and React experience...",
        "parsed_keywords": [
            {"keyword": "Python", "category": "technical", "importance": 0.9},
            {"keyword": "React", "category": "technical", "importance": 0.8}
        ],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    await test_db.job_descriptions.insert_one(job_data)
    return job_data
