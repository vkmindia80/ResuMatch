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
    skip: int = 0,
    limit: int = 50,
    job_description_id: Optional[str] = None,
    category: Optional[str] = None,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """
    Get interview questions with pagination
    
    Parameters:
    - skip: Number of records to skip (default: 0)
    - limit: Maximum number of records to return (default: 50, max: 200)
    - job_description_id: Filter by job description
    - category: Filter by question category
    """
    # Validate and cap limit
    limit = min(limit, 200)
    
    # Build query
    query = {"user_id": user_id}
    if job_description_id:
        query["job_description_id"] = job_description_id
    if category:
        query["category"] = category
    
    # Get total count
    total_count = await db.interview_questions.count_documents(query)
    
    # Get paginated questions
    cursor = db.interview_questions.find(query).sort("created_at", -1).skip(skip).limit(limit)
    questions = await cursor.to_list(length=limit)
    
    for question in questions:
        question.pop("_id", None)
    
    return {
        "items": questions,
        "total": total_count,
        "skip": skip,
        "limit": limit,
        "has_more": (skip + limit) < total_count
    }

@router.get("/questions-grouped")
async def get_questions_grouped_by_job(
    category: Optional[str] = None,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """
    Get interview questions grouped by job description
    
    Returns questions organized by job with metadata:
    - Jobs sorted by creation date (newest first)
    - Questions within each job sorted by creation date (newest first)
    - Optional category filter applied to questions
    """
    # Build question query
    question_query = {"user_id": user_id}
    if category:
        question_query["category"] = category
    
    # Get all questions for the user (with optional category filter)
    cursor = db.interview_questions.find(question_query).sort("created_at", -1)
    all_questions = await cursor.to_list(length=None)
    
    # Group questions by job_description_id
    job_question_map = {}
    for question in all_questions:
        question.pop("_id", None)
        job_id = question.get("job_description_id")
        if job_id not in job_question_map:
            job_question_map[job_id] = []
        job_question_map[job_id].append(question)
    
    # Get job details for all jobs that have questions
    job_ids = list(job_question_map.keys())
    jobs_cursor = db.job_descriptions.find({"id": {"$in": job_ids}, "user_id": user_id})
    jobs = await jobs_cursor.to_list(length=None)
    
    # Create job map for quick lookup
    job_map = {}
    for job in jobs:
        job.pop("_id", None)
        job_map[job["id"]] = job
    
    # Build grouped response
    grouped_data = []
    for job_id, questions in job_question_map.items():
        job_info = job_map.get(job_id)
        if not job_info:
            # Job might have been deleted, skip
            continue
        
        # Sort questions by created_at (newest first) - already sorted from query
        grouped_data.append({
            "job": {
                "id": job_info["id"],
                "title": job_info["title"],
                "company": job_info["company"],
                "location": job_info.get("location"),
                "job_type": job_info.get("job_type"),
                "created_at": job_info["created_at"]
            },
            "questions": questions,
            "question_count": len(questions),
            "generated_dates": list(set([q["created_at"].strftime("%Y-%m-%d %H:%M:%S") for q in questions]))
        })
    
    # Sort grouped data by job creation date (newest first)
    grouped_data.sort(key=lambda x: x["job"]["created_at"], reverse=True)
    
    return {
        "groups": grouped_data,
        "total_jobs": len(grouped_data),
        "total_questions": sum([g["question_count"] for g in grouped_data])
    }

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
