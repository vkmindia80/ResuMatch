from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from utils.auth import get_current_user_id
from utils.ai_job_parser import AIJobParser
from utils.job_match_scorer import JobMatchScorer
from database import get_database
from datetime import datetime
import uuid

router = APIRouter()

class JobDescriptionCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500, description="Job title")
    company: str = Field(..., min_length=1, max_length=200, description="Company name")
    location: Optional[str] = Field(None, max_length=200, description="Job location")
    job_type: Optional[str] = Field(None, max_length=100, description="Job type")
    description: str = Field(..., min_length=10, max_length=50000, description="Job description")

class JobDescriptionResponse(BaseModel):
    id: str
    user_id: str
    title: str
    company: str
    location: Optional[str]
    job_type: Optional[str]
    description: str
    parsed_data: Dict[str, Any] = {}
    parsed_keywords: List[str] = []
    created_at: datetime

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_job_description(
    job: JobDescriptionCreate,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """
    Create a new job description with AI-powered parsing
    """
    job_id = str(uuid.uuid4())
    
    # AI-powered job parsing
    parser = AIJobParser()
    job_data_dict = {
        "title": job.title,
        "company": job.company,
        "location": job.location,
        "job_type": job.job_type,
        "description": job.description
    }
    
    parse_result = await parser.parse_job_description(job_data_dict)
    parsed_data = parse_result.get("data", {})
    
    # Extract keywords from parsed data
    keywords = []
    keywords.extend(parsed_data.get("technical_skills", []))
    keywords.extend(parsed_data.get("tools_and_technologies", []))
    keywords.extend(parsed_data.get("required_skills", []))
    # Remove duplicates and limit
    keywords = list(set(keywords))[:30]
    
    job_dict = {
        "id": job_id,
        "user_id": user_id,
        "title": job.title,
        "company": job.company,
        "location": job.location,
        "job_type": job.job_type,
        "description": job.description,
        "parsed_data": parsed_data,
        "parsed_keywords": keywords,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    await db.job_descriptions.insert_one(job_dict)
    
    job_dict.pop("_id", None)
    return job_dict

@router.get("/")
async def get_job_descriptions(
    skip: int = 0,
    limit: int = 20,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """
    Get all job descriptions for current user with pagination
    
    Parameters:
    - skip: Number of records to skip (default: 0)
    - limit: Maximum number of records to return (default: 20, max: 100)
    """
    # Validate and cap limit
    limit = min(limit, 100)
    
    # Get total count
    total_count = await db.job_descriptions.count_documents({"user_id": user_id})
    
    # Get paginated jobs
    cursor = db.job_descriptions.find({"user_id": user_id}).sort("created_at", -1).skip(skip).limit(limit)
    jobs = await cursor.to_list(length=limit)
    
    for job in jobs:
        job.pop("_id", None)
    
    return {
        "items": jobs,
        "total": total_count,
        "skip": skip,
        "limit": limit,
        "has_more": (skip + limit) < total_count
    }

@router.get("/{job_id}")
async def get_job_description(
    job_id: str,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """
    Get a specific job description
    """
    job = await db.job_descriptions.find_one({"id": job_id, "user_id": user_id})
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job description not found"
        )
    
    job.pop("_id", None)
    return job

@router.put("/{job_id}")
async def update_job_description(
    job_id: str,
    job: JobDescriptionCreate,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """
    Update a job description
    """
    # Check if job exists
    existing_job = await db.job_descriptions.find_one({"id": job_id, "user_id": user_id})
    if not existing_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job description not found"
        )
    
    # Re-parse job with updated data if description changed
    parser = AIJobParser()
    job_data_dict = {
        "title": job.title,
        "company": job.company,
        "location": job.location,
        "job_type": job.job_type,
        "description": job.description
    }
    
    parse_result = await parser.parse_job_description(job_data_dict)
    parsed_data = parse_result.get("data", {})
    
    # Extract keywords
    keywords = []
    keywords.extend(parsed_data.get("technical_skills", []))
    keywords.extend(parsed_data.get("tools_and_technologies", []))
    keywords.extend(parsed_data.get("required_skills", []))
    keywords = list(set(keywords))[:30]
    
    # Update job
    update_data = {
        "title": job.title,
        "company": job.company,
        "location": job.location,
        "job_type": job.job_type,
        "description": job.description,
        "parsed_data": parsed_data,
        "parsed_keywords": keywords,
        "updated_at": datetime.utcnow()
    }
    
    await db.job_descriptions.update_one(
        {"id": job_id, "user_id": user_id},
        {"$set": update_data}
    )
    
    # Return updated job
    updated_job = await db.job_descriptions.find_one({"id": job_id, "user_id": user_id})
    updated_job.pop("_id", None)
    
    return updated_job

@router.delete("/{job_id}")
async def delete_job_description(
    job_id: str,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """
    Delete a job description
    """
    result = await db.job_descriptions.delete_one({"id": job_id, "user_id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job description not found"
        )
    
    return {"message": "Job description deleted successfully"}

@router.get("/{job_id}/match-score")
async def get_job_match_score(
    job_id: str,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """
    Calculate match score between user profile and job description
    """
    # Get job description
    job = await db.job_descriptions.find_one({"id": job_id, "user_id": user_id})
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
            detail="Profile not found. Please create a profile first."
        )
    
    # Calculate match score
    scorer = JobMatchScorer()
    match_score = scorer.calculate_match_score(profile, job)
    
    return match_score

