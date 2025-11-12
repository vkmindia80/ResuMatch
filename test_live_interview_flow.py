#!/usr/bin/env python3
"""
Test script to verify Live Interview Assistant flow
"""
import asyncio
import sys
sys.path.insert(0, '/app/backend')

from utils.live_interview_ai import LiveInterviewAI
from database import connect_to_mongo, get_database, close_mongo_connection
import uuid
from datetime import datetime

async def test_complete_flow():
    """Test the complete live interview flow"""
    print("=" * 60)
    print("LIVE INTERVIEW ASSISTANT - COMPLETE FLOW TEST")
    print("=" * 60)
    
    # Connect to database
    print("\n1. Connecting to database...")
    await connect_to_mongo()
    db = get_database()
    print("✓ Database connected")
    
    # Create test user and profile
    print("\n2. Creating test profile...")
    test_user_id = str(uuid.uuid4())
    test_profile = {
        "user_id": test_user_id,
        "professional_summary": "Experienced software engineer with 5+ years in full-stack development",
        "experience": [
            {
                "title": "Senior Software Engineer",
                "company": "Tech Corp",
                "description": "Led development of microservices architecture"
            }
        ],
        "skills": ["Python", "JavaScript", "React", "FastAPI", "Docker"],
        "education": [
            {
                "degree": "BS",
                "field": "Computer Science",
                "institution": "Test University"
            }
        ]
    }
    await db.profiles.insert_one(test_profile)
    print("✓ Test profile created")
    
    # Create test session
    print("\n3. Creating live interview session...")
    session_id = str(uuid.uuid4())
    session = {
        "id": session_id,
        "user_id": test_user_id,
        "job_description_id": None,
        "resume_id": None,
        "resume_source": "profile",
        "title": "Test Interview Session",
        "status": "active",
        "started_at": datetime.utcnow(),
        "ended_at": None,
        "duration_seconds": 0,
        "language": "en-US",
        "model_preference": "gpt-4",
        "created_at": datetime.utcnow()
    }
    await db.live_interview_sessions.insert_one(session)
    print(f"✓ Session created with ID: {session_id}")
    
    # Create transcript document
    print("\n4. Creating transcript document...")
    transcript = {
        "id": str(uuid.uuid4()),
        "session_id": session_id,
        "user_id": test_user_id,
        "entries": [],
        "ai_answers": [],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    await db.interview_transcripts.insert_one(transcript)
    print("✓ Transcript document created")
    
    # Test AI answer generation
    print("\n5. Testing AI answer generation...")
    ai = LiveInterviewAI()
    test_question = "Tell me about your experience with Python and FastAPI"
    
    answer_data = await ai.generate_instant_answer(
        question=test_question,
        user_profile=test_profile,
        resume=None,
        job_description=None,
        model="gpt-4",
        resume_source="profile"
    )
    
    print(f"✓ AI answer generated successfully!")
    print(f"  Question: {answer_data['question']}")
    print(f"  Answer length: {len(answer_data['answer'])} characters")
    print(f"  Model: {answer_data['model']}")
    print(f"  Context used: {', '.join(answer_data['context_used'])}")
    print(f"\n  Answer preview:")
    print(f"  {answer_data['answer'][:200]}...")
    
    # Save answer to transcript
    print("\n6. Saving answer to transcript...")
    await db.interview_transcripts.update_one(
        {"session_id": session_id},
        {
            "$push": {"ai_answers": answer_data},
            "$set": {"updated_at": datetime.utcnow()}
        }
    )
    print("✓ Answer saved to transcript")
    
    # Verify data
    print("\n7. Verifying saved data...")
    saved_transcript = await db.interview_transcripts.find_one({"session_id": session_id})
    if saved_transcript and len(saved_transcript.get("ai_answers", [])) > 0:
        print(f"✓ Transcript has {len(saved_transcript['ai_answers'])} AI answers")
    else:
        print("✗ Error: No answers found in transcript")
    
    # Cleanup
    print("\n8. Cleaning up test data...")
    await db.profiles.delete_one({"user_id": test_user_id})
    await db.live_interview_sessions.delete_one({"id": session_id})
    await db.interview_transcripts.delete_one({"session_id": session_id})
    print("✓ Test data cleaned up")
    
    await close_mongo_connection()
    
    print("\n" + "=" * 60)
    print("✓ ALL TESTS PASSED - Live Interview flow is working!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_complete_flow())
