from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from typing import List, Optional
from utils.auth import get_current_user_id
from server import get_database
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
    Generate interview questions based on job description and user profile
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
    
    # Generate basic questions (will be enhanced with AI)
    questions = generate_basic_questions(job, profile, request.count)
    
    # Save questions to database
    for question in questions:
        question["user_id"] = user_id
        question["job_description_id"] = request.job_description_id
        question["created_at"] = datetime.utcnow()
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

def generate_basic_questions(job: dict, profile: dict, count: int) -> List[dict]:
    """
    Generate basic interview questions (will be enhanced with AI)
    """
    questions_bank = [
        # Behavioral
        {
            "id": str(uuid.uuid4()),
            "question": "Tell me about a time when you had to work with a difficult team member.",
            "category": "behavioral",
            "difficulty": "medium"
        },
        {
            "id": str(uuid.uuid4()),
            "question": "Describe a situation where you had to meet a tight deadline.",
            "category": "behavioral",
            "difficulty": "medium"
        },
        {
            "id": str(uuid.uuid4()),
            "question": "Tell me about a time you failed and what you learned from it.",
            "category": "behavioral",
            "difficulty": "hard"
        },
        # Technical
        {
            "id": str(uuid.uuid4()),
            "question": f"What experience do you have with {job.get('title', 'this role')}?",
            "category": "technical",
            "difficulty": "medium"
        },
        # Culture Fit
        {
            "id": str(uuid.uuid4()),
            "question": f"Why do you want to work at {job.get('company', 'our company')}?",
            "category": "culture_fit",
            "difficulty": "easy"
        },
        {
            "id": str(uuid.uuid4()),
            "question": "What are you looking for in your next role?",
            "category": "culture_fit",
            "difficulty": "easy"
        },
        # Common
        {
            "id": str(uuid.uuid4()),
            "question": "Tell me about yourself.",
            "category": "common",
            "difficulty": "easy"
        },
        {
            "id": str(uuid.uuid4()),
            "question": "What are your greatest strengths?",
            "category": "common",
            "difficulty": "easy"
        },
        {
            "id": str(uuid.uuid4()),
            "question": "What are your weaknesses?",
            "category": "common",
            "difficulty": "medium"
        },
        {
            "id": str(uuid.uuid4()),
            "question": "Where do you see yourself in 5 years?",
            "category": "common",
            "difficulty": "medium"
        }
    ]
    
    # Return requested count or all questions if count is higher
    return questions_bank[:min(count, len(questions_bank))]
