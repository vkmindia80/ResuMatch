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
    source_resume_id: Optional[str] = None  # If provided, optimize existing resume instead of generating from profile

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
    Generate AI-optimized resume based on:
    1. Profile + Job Description (default)
    2. Existing Resume + Job Description (if source_resume_id provided)
    
    Both paths go through iterative ATS optimization for 95%+ scores
    """
    
    # Check if re-optimizing existing resume or generating from profile
    is_reoptimization = bool(resume_data.source_resume_id)
    
    if is_reoptimization:
        # Mode 1: Re-optimize existing resume for new job
        print(f"🔄 Re-optimizing existing resume {resume_data.source_resume_id} for new job...")
        
        source_resume = await db.resumes.find_one({
            "id": resume_data.source_resume_id,
            "user_id": user_id
        })
        
        if not source_resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Source resume not found"
            )
        
        # Validate job description is provided for re-optimization
        if not resume_data.job_description_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Job description is required when re-optimizing an existing resume"
            )
        
        # Get profile for reference
        profile = await db.profiles.find_one({"user_id": user_id})
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
    else:
        # Mode 2: Generate from profile (original flow)
        print("✨ Generating new resume from profile...")
        
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
    
    # Generate or extract initial content based on mode
    if is_reoptimization:
        # Use existing resume content as starting point but RE-OPTIMIZE with AI for new job
        print("📋 Re-optimizing existing resume with AI for new job description...")
        source_content = source_resume.get("content", {})
        source_ats = source_resume.get("ats_score", {})
        source_score = source_ats.get("overall_score", 0)
        
        print(f"   Source Resume ATS Score: {source_score}%")
        print(f"   Target: Beat or match {source_score}% with better job alignment")
        print(f"   Optimizing for: {job_description.get('title') if job_description else 'General'}")
        
        # Initialize AI generator for re-optimization
        ai_generator = AIResumeGenerator()
        
        # CRITICAL: Regenerate content with AI for the NEW job description
        print("   🤖 Regenerating summary for new job...")
        summary = await ai_generator.generate_professional_summary(profile, job_description)
        
        print("   🤖 Re-optimizing experience bullets for new job keywords...")
        # Use existing experience but re-optimize bullets for new job
        existing_experience = source_content.get("experience", [])
        optimized_experience = await ai_generator.optimize_experience_bullets(
            existing_experience,
            job_description
        )
        
        print("   🤖 Re-prioritizing skills for new job requirements...")
        existing_skills = source_content.get("skills", {})
        optimized_skills = await ai_generator.generate_skills_optimization(
            existing_skills,
            job_description
        )
        
        print(f"   ✅ AI re-optimization complete - content adapted for new role")
        
    else:
        # Generate fresh content from profile
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
    
    # If re-optimizing, pass source score as minimum target
    min_target = None
    if is_reoptimization and source_resume:
        source_ats = source_resume.get("ats_score", {})
        min_target = source_ats.get("overall_score", 0)
    
    try:
        optimized_content, final_ats_score, iterations = await optimizer.optimize_resume_iteratively(
            resume_content,
            initial_ats_score,
            job_description,
            min_target_score=min_target
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
    
    # Generate descriptive name with date & time stamp
    now = datetime.utcnow()
    timestamp_str = now.strftime("%m/%d/%Y %I:%M %p")  # Format: 11/07/2025 03:45 PM
    
    # Create resume name
    if is_reoptimization:
        # For re-optimized resumes
        if job_description:
            resume_name = f"Resume for {job_description.get('title', 'Position')} - {timestamp_str}"
        else:
            resume_name = f"Optimized Resume - {timestamp_str}"
    else:
        # For new resumes
        if job_description:
            resume_name = f"Resume for {job_description.get('title', 'Position')} - {timestamp_str}"
        else:
            resume_name = f"Resume - {timestamp_str}"
    
    # If re-optimization, compare with source resume score
    source_score = None
    score_improvement = None
    if is_reoptimization and source_resume:
        source_score = source_resume.get("ats_score", {}).get("overall_score", 0)
        current_score = ats_score.get("overall_score", 0)
        score_improvement = current_score - source_score
        
        print(f"\n📊 Re-optimization Comparison:")
        print(f"   Source Resume Score: {source_score}%")
        print(f"   New Resume Score: {current_score}%")
        print(f"   Improvement: {'+' if score_improvement >= 0 else ''}{score_improvement:.1f}%")
        
        if score_improvement >= 0:
            print(f"   ✅ Success! Better or equal score achieved.")
        else:
            print(f"   ⚠️  Warning: Score decreased. Using new version anyway (may have better job match).")
    
    resume_dict = {
        "id": resume_id,
        "user_id": user_id,
        "profile_id": profile.get("id"),
        "job_description_id": resume_data.job_description_id,
        "template_id": resume_data.template_id,
        "name": resume_name,  # Add descriptive name with timestamp
        "status": "draft",
        "content": resume_content,
        "ats_score": ats_score,
        "source_resume_id": resume_data.source_resume_id if is_reoptimization else None,
        "source_resume_score": source_score,  # Track original score
        "score_improvement": score_improvement,  # Track improvement
        "is_reoptimized": is_reoptimization,
        "generated_at": now,
        "created_at": now,
        "updated_at": now
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


@router.get("/{resume_id}/intelligence/performance")
async def get_resume_performance_analysis(
    resume_id: str,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """
    Get performance analysis for a resume compared to user's other resumes
    """
    from utils.resume_intelligence import ResumeIntelligence
    
    # Get the specific resume
    resume = await db.resumes.find_one({"id": resume_id, "user_id": user_id})
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    # Get all user's resumes
    cursor = db.resumes.find({"user_id": user_id})
    all_resumes = await cursor.to_list(length=100)
    
    # Analyze performance
    intelligence = ResumeIntelligence()
    analysis = intelligence.analyze_resume_performance(resume, all_resumes)
    
    return analysis


@router.get("/{resume_id}/intelligence/ab-suggestions")
async def get_ab_testing_suggestions(
    resume_id: str,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """
    Get A/B testing suggestions for resume optimization
    """
    from utils.resume_intelligence import ResumeIntelligence
    
    # Get the resume
    resume = await db.resumes.find_one({"id": resume_id, "user_id": user_id})
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    # Generate suggestions
    intelligence = ResumeIntelligence()
    suggestions = intelligence.generate_ab_testing_suggestions(resume)
    
    return {"suggestions": suggestions}


@router.post("/intelligence/compare")
async def compare_two_resumes(
    resume_a_id: str,
    resume_b_id: str,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """
    Compare two resumes side-by-side with full content and visual differences
    
    Query Parameters:
    - resume_a_id: ID of first resume
    - resume_b_id: ID of second resume
    """
    from utils.resume_intelligence import ResumeIntelligence
    
    # Get both resumes
    resume_a = await db.resumes.find_one({"id": resume_a_id, "user_id": user_id})
    resume_b = await db.resumes.find_one({"id": resume_b_id, "user_id": user_id})
    
    if not resume_a or not resume_b:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or both resumes not found"
        )
    
    # Compare resumes
    intelligence = ResumeIntelligence()
    comparison = intelligence.compare_resumes(resume_a, resume_b)
    
    # Add full content for side-by-side display
    comparison["resume_a_full"] = {
        "id": resume_a.get("id"),
        "name": resume_a.get("name"),
        "content": resume_a.get("content", {}),
        "ats_score": resume_a.get("ats_score", {}),
        "created_at": resume_a.get("created_at"),
        "is_reoptimized": resume_a.get("is_reoptimized", False),
        "score_improvement": resume_a.get("score_improvement")
    }
    
    comparison["resume_b_full"] = {
        "id": resume_b.get("id"),
        "name": resume_b.get("name"),
        "content": resume_b.get("content", {}),
        "ats_score": resume_b.get("ats_score", {}),
        "created_at": resume_b.get("created_at"),
        "is_reoptimized": resume_b.get("is_reoptimized", False),
        "score_improvement": resume_b.get("score_improvement")
    }
    
    return comparison


@router.get("/intelligence/compare-with-profile/{resume_id}")
async def compare_resume_with_profile(
    resume_id: str,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """
    Compare a resume with the user's profile to show what changed
    """
    # Get resume
    resume = await db.resumes.find_one({"id": resume_id, "user_id": user_id})
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    # Get profile
    profile = await db.profiles.find_one({"user_id": user_id})
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    # Format profile data similar to resume for comparison
    profile_formatted = {
        "header": profile.get("personal_info", {}),
        "summary": "[Generated by AI from your profile data]",
        "experience": profile.get("experience", []),
        "education": profile.get("education", []),
        "skills": profile.get("skills", {}),
        "projects": profile.get("projects", []),
        "certifications": profile.get("certifications", [])
    }
    
    resume_content = resume.get("content", {})
    
    # Compare and find differences
    differences = {
        "summary": {
            "profile": profile_formatted.get("summary", ""),
            "resume": resume_content.get("summary", ""),
            "changed": True  # Always changed since AI generates it
        },
        "experience_changes": [],
        "skills_changes": {
            "profile_technical": profile_formatted.get("skills", {}).get("technical", []),
            "resume_technical": resume_content.get("skills", {}).get("technical", []),
            "profile_soft": profile_formatted.get("skills", {}).get("soft", []),
            "resume_soft": resume_content.get("skills", {}).get("soft", [])
        }
    }
    
    # Compare experience bullets
    profile_exp = profile_formatted.get("experience", [])
    resume_exp = resume_content.get("experience", [])
    
    for idx in range(max(len(profile_exp), len(resume_exp))):
        if idx < len(profile_exp) and idx < len(resume_exp):
            p_exp = profile_exp[idx]
            r_exp = resume_exp[idx]
            
            differences["experience_changes"].append({
                "company": p_exp.get("company"),
                "title": p_exp.get("title"),
                "profile_bullets": p_exp.get("responsibilities", []),
                "resume_bullets": r_exp.get("optimized_responsibilities", r_exp.get("responsibilities", []))
            })
    
    return {
        "profile_data": profile_formatted,
        "resume_data": resume_content,
        "differences": differences,
        "resume_info": {
            "id": resume.get("id"),
            "name": resume.get("name"),
            "ats_score": resume.get("ats_score", {}),
            "created_at": resume.get("created_at")
        }
    }


@router.get("/{resume_id}/intelligence/industry-optimization")
async def get_industry_optimization(
    resume_id: str,
    target_industry: str,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """
    Get industry-specific optimization recommendations
    
    Query Parameters:
    - target_industry: Target industry (tech, finance, healthcare, marketing, general)
    """
    from utils.resume_intelligence import ResumeIntelligence
    
    # Get the resume
    resume = await db.resumes.find_one({"id": resume_id, "user_id": user_id})
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    # Get industry optimization
    intelligence = ResumeIntelligence()
    optimization = intelligence.get_industry_optimization(resume, target_industry)
    
    return optimization
