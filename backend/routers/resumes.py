from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from typing import Optional, List
from utils.auth import get_current_user_id
from database import get_database
from datetime import datetime
import uuid

router = APIRouter()

class ResumeCreate(BaseModel):
    job_description_id: Optional[str] = None
    template_id: str = "template_1"

class ResumeResponse(BaseModel):
    id: str
    user_id: str
    profile_id: Optional[str]
    job_description_id: Optional[str]
    template_id: str
    status: str
    ats_score: int
    created_at: datetime

@router.post("/generate", status_code=status.HTTP_201_CREATED)
async def generate_resume(
    resume_data: ResumeCreate,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """
    Generate a new resume based on profile and job description
    """
    # Get user profile
    profile = await db.profiles.find_one({"user_id": user_id})
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found. Please create a profile first."
        )
    
    # Get job description if provided
    job_description = None
    if resume_data.job_description_id:
        job_description = await db.job_descriptions.find_one({
            "id": resume_data.job_description_id,
            "user_id": user_id
        })
    
    resume_id = str(uuid.uuid4())
    
    # Basic resume structure (will be enhanced with AI)
    resume_dict = {
        "id": resume_id,
        "user_id": user_id,
        "profile_id": profile["id"],
        "job_description_id": resume_data.job_description_id,
        "template_id": resume_data.template_id,
        "status": "draft",
        "content": {
            "header": profile.get("personal_info", {}),
            "summary": generate_summary(profile, job_description),
            "experience": profile.get("experience", []),
            "education": profile.get("education", []),
            "skills": profile.get("skills", {}),
            "projects": profile.get("projects", []),
            "certifications": profile.get("certifications", [])
        },
        "ats_score": calculate_basic_ats_score(profile, job_description),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    await db.resumes.insert_one(resume_dict)
    
    resume_dict.pop("_id", None)
    return resume_dict

@router.get("/")
async def get_resumes(
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """
    Get all resumes for current user
    """
    cursor = db.resumes.find({"user_id": user_id})
    resumes = await cursor.to_list(length=100)
    
    for resume in resumes:
        resume.pop("_id", None)
    
    return resumes

@router.get("/{resume_id}")
async def get_resume(
    resume_id: str,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """
    Get a specific resume
    """
    resume = await db.resumes.find_one({"id": resume_id, "user_id": user_id})
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    resume.pop("_id", None)
    return resume

@router.delete("/{resume_id}")
async def delete_resume(
    resume_id: str,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """
    Delete a resume
    """
    result = await db.resumes.delete_one({"id": resume_id, "user_id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    return {"message": "Resume deleted successfully"}

@router.get("/templates/list")
async def get_templates():
    """
    Get available resume templates
    """
    templates = [
        {"id": "template_1", "name": "Professional", "description": "Clean and modern design"},
        {"id": "template_2", "name": "Creative", "description": "Bold and eye-catching"},
        {"id": "template_3", "name": "Executive", "description": "Sophisticated and elegant"},
        {"id": "template_4", "name": "Technical", "description": "Perfect for developers"},
        {"id": "template_5", "name": "Minimalist", "description": "Simple and focused"}
    ]
    return templates

def generate_summary(profile: dict, job_description: Optional[dict]) -> str:
    """
    Generate a basic professional summary (will be enhanced with AI)
    """
    personal_info = profile.get("personal_info", {})
    title = personal_info.get("title", "Professional")
    experience_count = len(profile.get("experience", []))
    
    summary = f"{title} with {experience_count}+ years of experience."
    return summary

def calculate_basic_ats_score(profile: dict, job_description: Optional[dict]) -> int:
    """
    Calculate basic ATS score (will be enhanced with AI)
    """
    score = 50  # Base score
    
    # Add points for complete sections
    if profile.get("experience"):
        score += 15
    if profile.get("education"):
        score += 10
    if profile.get("skills"):
        score += 15
    if profile.get("certifications"):
        score += 5
    if profile.get("projects"):
        score += 5
    
    return min(score, 100)
