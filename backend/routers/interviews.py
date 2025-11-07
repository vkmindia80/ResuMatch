from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from typing import List, Optional
from utils.auth import get_current_user_id
from utils.ai_interview_generator import AIInterviewGenerator
from database import get_database
from datetime import datetime
import uuid

router = APIRouter()

class GenerateQuestionsRequest(BaseModel):
    job_description_id: str
    count: int = 25

class InterviewQuestionResponse(BaseModel):
    id: str
    question: str
    category: str
    difficulty: str
    ai_generated_answer: Optional[dict] = None

@router.post("/generate-questions", status_code=status.HTTP_201_CREATED)
async def generate_interview_questions(
    request: GenerateQuestionsRequest,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """
    Generate AI-powered interview questions with STAR-format answers
    """
    # Get job description
    job = await db.job_descriptions.find_one({
        "id": request.job_description_id,
        "user_id": user_id
    })
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job description not found"
        )
    
    # Get user profile
    profile = await db.profiles.find_one({"user_id": user_id})
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    # Generate AI-powered questions
    print(f"Generating {request.count} AI-powered interview questions...")
    ai_generator = AIInterviewGenerator()
    questions = await ai_generator.generate_interview_questions(job, profile, request.count)
    
    if not questions:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate interview questions. Please try again."
        )
    
    # Add IDs and save questions to database
    for question in questions:
        question["id"] = str(uuid.uuid4())
        question["user_id"] = user_id
        question["job_description_id"] = request.job_description_id
        question["created_at"] = datetime.utcnow()
        question["is_favorite"] = False
        question["practice_count"] = 0
        question["user_custom_answer"] = None
        question["last_practiced"] = None
        
        await db.interview_questions.insert_one(question)
        question.pop("_id", None)
    
    return {"count": len(questions), "questions": questions}

@router.get("/questions")
async def get_interview_questions(
    job_description_id: Optional[str] = None,
    category: Optional[str] = None,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """
    Get interview questions
    """
    query = {"user_id": user_id}
    if job_description_id:
        query["job_description_id"] = job_description_id
    if category:
        query["category"] = category
    
    cursor = db.interview_questions.find(query)
    questions = await cursor.to_list(length=200)
    
    for question in questions:
        question.pop("_id", None)
    
    return questions

@router.get("/categories")
async def get_question_categories():
    """
    Get available question categories
    """
    categories = [
        {"id": "behavioral", "name": "Behavioral", "description": "Questions about past experiences"},
        {"id": "technical", "name": "Technical", "description": "Role-specific technical questions"},
        {"id": "culture_fit", "name": "Culture Fit", "description": "Questions about values and work style"},
        {"id": "situational", "name": "Situational", "description": "Hypothetical scenario questions"},
        {"id": "common", "name": "Common", "description": "Frequently asked interview questions"}
    ]
    return categories
