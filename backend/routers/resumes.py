from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from utils.auth import get_current_user_id
from utils.ai_resume_generator import AIResumeGenerator
from utils.ats_scorer import ATSScorer
from utils.ats_optimizer import ATSOptimizer
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
    ats_score: Dict[str, Any]
    created_at: datetime

@router.post("/generate", status_code=status.HTTP_201_CREATED)
async def generate_resume(
    resume_data: ResumeCreate,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """
    Generate AI-optimized resume based on profile and job description
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
    
    # Initialize AI generator
    ai_generator = AIResumeGenerator()
    
    # Generate AI-powered content
    print("Generating professional summary with AI...")
    summary = await ai_generator.generate_professional_summary(profile, job_description)
    
    print("Optimizing experience bullets with AI...")
    optimized_experience = await ai_generator.optimize_experience_bullets(
        profile.get("experience", []),
        job_description
    )
    
    print("Optimizing skills prioritization...")
    optimized_skills = await ai_generator.generate_skills_optimization(
        profile.get("skills", {}),
        job_description
    )
    
    # Normalize skills format to ensure frontend compatibility
    def normalize_skills_list(skills_list):
        """Convert skill objects to simple strings for frontend compatibility"""
        if not skills_list:
            return []
        normalized = []
        for skill in skills_list:
            if isinstance(skill, dict):
                # Extract name from object
                skill_name = skill.get("name") or skill.get("skill") or ""
                if skill_name:
                    normalized.append(skill_name)
            elif isinstance(skill, str):
                normalized.append(skill)
        return normalized
    
    # Normalize technical and soft skills to string arrays
    if optimized_skills:
        if "technical" in optimized_skills:
            optimized_skills["technical"] = normalize_skills_list(optimized_skills["technical"])
        if "soft" in optimized_skills:
            optimized_skills["soft"] = normalize_skills_list(optimized_skills["soft"])
        if "tools" in optimized_skills:
            optimized_skills["tools"] = normalize_skills_list(optimized_skills["tools"])
        if "languages" in optimized_skills:
            # Keep languages as objects but ensure they have proper format
            langs = []
            for lang in optimized_skills.get("languages", []):
                if isinstance(lang, dict):
                    langs.append(lang)
                elif isinstance(lang, str):
                    langs.append({"name": lang, "fluency": "proficient"})
            optimized_skills["languages"] = langs
    
    # Build resume content
    resume_content = {
        "header": profile.get("personal_info", {}),
        "summary": summary,
        "experience": optimized_experience,
        "education": profile.get("education", []),
        "skills": optimized_skills,
        "projects": profile.get("projects", []),
        "certifications": profile.get("certifications", [])
    }
    
    # Calculate initial ATS score
    print("Calculating initial ATS score...")
    ats_scorer = ATSScorer()
    initial_ats_score = ats_scorer.calculate_ats_score(resume_content, job_description)
    
    print(f"Initial ATS score: {initial_ats_score.get('overall_score', 0)}%")
    
    # Run iterative optimization to achieve 95%+ score
    print("Starting iterative ATS optimization for perfect score...")
    optimizer = ATSOptimizer()
    
    try:
        optimized_content, final_ats_score, iterations = await optimizer.optimize_resume_iteratively(
            resume_content,
            initial_ats_score,
            job_description
        )
        
        print(f"✅ Optimization complete! Final score: {final_ats_score.get('overall_score', 0)}% (after {iterations} iterations)")
        
        # Use optimized content and score
        resume_content = optimized_content
        ats_score = final_ats_score
        
    except Exception as e:
        print(f"⚠️ Optimization error: {e}")
        print("Falling back to initial content...")
        # Fall back to initial content if optimization fails
        ats_score = initial_ats_score
    
    resume_dict = {
        "id": resume_id,
        "user_id": user_id,
        "profile_id": profile.get("id"),
        "job_description_id": resume_data.job_description_id,
        "template_id": resume_data.template_id,
        "status": "draft",
        "content": resume_content,
        "ats_score": ats_score,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    await db.resumes.insert_one(resume_dict)
    
    resume_dict.pop("_id", None)
    return resume_dict

@router.get("/")
async def get_resumes(
    skip: int = 0,
    limit: int = 20,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """
    Get all resumes for current user with pagination
    
    Parameters:
    - skip: Number of records to skip (default: 0)
    - limit: Maximum number of records to return (default: 20, max: 100)
    """
    # Validate and cap limit
    limit = min(limit, 100)
    
    # Get total count
    total_count = await db.resumes.count_documents({"user_id": user_id})
    
    # Get paginated resumes
    cursor = db.resumes.find({"user_id": user_id}).sort("created_at", -1).skip(skip).limit(limit)
    resumes = await cursor.to_list(length=limit)
    
    for resume in resumes:
        resume.pop("_id", None)
    
    return {
        "items": resumes,
        "total": total_count,
        "skip": skip,
        "limit": limit,
        "has_more": (skip + limit) < total_count
    }

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
