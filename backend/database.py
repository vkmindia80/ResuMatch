from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime
import uuid

# Global database variables
db_client = None
db = None

async def create_demo_user():
    """Create demo user for testing if it doesn't exist"""
    try:
        from utils.auth import get_password_hash
        
        demo_email = "demo@resumatch.com"
        demo_password = "Demo@123"
        
        # Check if demo user already exists
        existing_demo = await db.users.find_one({"email": demo_email})
        
        if not existing_demo:
            # Create demo user
            demo_user = {
                "id": str(uuid.uuid4()),
                "email": demo_email,
                "full_name": "Demo User",
                "password_hash": get_password_hash(demo_password),
                "is_verified": True,
                "subscription_tier": "free",
                "google_id": None,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "last_login": None
            }
            
            await db.users.insert_one(demo_user)
            print(f"✅ Demo user created: {demo_email} / {demo_password}")
        else:
            print(f"✅ Demo user already exists: {demo_email}")
    except Exception as e:
        print(f"⚠️ Error creating demo user: {e}")

async def connect_to_mongo():
    """Connect to MongoDB"""
    global db_client, db
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017/resumatch')
    db_client = AsyncIOMotorClient(mongo_url)
    db = db_client.get_database()
    
    # Create indexes for performance
    # Users
    await db.users.create_index("email", unique=True)
    await db.users.create_index("created_at")
    await db.users.create_index([("email", 1), ("google_id", 1)])
    
    # Profiles
    await db.profiles.create_index("user_id", unique=True)
    await db.profiles.create_index("completeness_score")
    
    # Job Descriptions
    await db.job_descriptions.create_index("user_id")
    await db.job_descriptions.create_index([("user_id", 1), ("created_at", -1)])
    await db.job_descriptions.create_index("id")
    
    # Resumes
    await db.resumes.create_index("user_id")
    await db.resumes.create_index([("user_id", 1), ("created_at", -1)])
    await db.resumes.create_index("id")
    await db.resumes.create_index([("user_id", 1), ("job_description_id", 1)])
    
    # Interview Questions
    await db.interview_questions.create_index("user_id")
    await db.interview_questions.create_index([("user_id", 1), ("created_at", -1)])
    await db.interview_questions.create_index([("user_id", 1), ("job_description_id", 1)])
    await db.interview_questions.create_index([("user_id", 1), ("category", 1)])
    
    print("✅ Connected to MongoDB")
    print(f"✅ Database: {db.name}")
    
    # Create demo user for testing
    await create_demo_user()

async def close_mongo_connection():
    """Close MongoDB connection"""
    global db_client
    if db_client:
        db_client.close()
        print("❌ Disconnected from MongoDB")

def get_database():
    """Get database instance"""
    return db
