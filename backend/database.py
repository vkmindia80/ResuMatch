from motor.motor_asyncio import AsyncIOMotorClient
import os

# Global database variables
db_client = None
db = None

async def connect_to_mongo():
    """Connect to MongoDB"""
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

async def close_mongo_connection():
    """Close MongoDB connection"""
    global db_client
    if db_client:
        db_client.close()
        print("❌ Disconnected from MongoDB")

def get_database():
    """Get database instance"""
    return db
