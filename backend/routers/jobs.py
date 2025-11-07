from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from typing import List, Optional
from utils.auth import get_current_user_id
from server import get_database
from datetime import datetime
import uuid

router = APIRouter()

class JobDescriptionCreate(BaseModel):
    title: str
    company: str
    location: Optional[str] = None
    job_type: Optional[str] = None
    description: str

class JobDescriptionResponse(BaseModel):
    id: str
    user_id: str
    title: str
    company: str
    location: Optional[str]
    job_type: Optional[str]
    description: str
    parsed_keywords: List[str] = []
    created_at: datetime

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_job_description(
    job: JobDescriptionCreate,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """
    Create a new job description
    """
    job_id = str(uuid.uuid4())
    
    # Basic keyword extraction (will enhance with AI later)
    keywords = extract_keywords(job.description)
    
    job_dict = {
        "id": job_id,
        "user_id": user_id,
        "title": job.title,
        "company": job.company,
        "location": job.location,
        "job_type": job.job_type,
        "description": job.description,
        "parsed_keywords": keywords,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    await db.job_descriptions.insert_one(job_dict)
    
    job_dict.pop("_id", None)
    return job_dict

@router.get("/")
async def get_job_descriptions(
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """
    Get all job descriptions for current user
    """
    cursor = db.job_descriptions.find({"user_id": user_id})
    jobs = await cursor.to_list(length=100)
    
    for job in jobs:
        job.pop("_id", None)
    
    return jobs

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

def extract_keywords(text: str) -> List[str]:
    """
    Basic keyword extraction (will be enhanced with AI)
    """
    # Common tech keywords
    tech_keywords = [
        "python", "javascript", "java", "react", "node", "angular", "vue",
        "sql", "mongodb", "aws", "docker", "kubernetes", "git", "agile",
        "machine learning", "ai", "data science", "api", "rest", "graphql"
    ]
    
    text_lower = text.lower()
    found_keywords = []
    
    for keyword in tech_keywords:
        if keyword in text_lower:
            found_keywords.append(keyword)
    
    return found_keywords
