from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
from utils.auth import get_current_user_id
from utils.ai_cover_letter_generator import AICoverLetterGenerator
from database import get_database
from datetime import datetime
import uuid

router = APIRouter()


class CoverLetterCreate(BaseModel):
    job_description_id: str
    tone: Optional[str] = "professional"  # professional, enthusiastic, formal
    template: Optional[str] = "standard"  # standard, creative, executive


class CoverLetterUpdate(BaseModel):
    content: Optional[Dict[str, Any]] = None
    tone: Optional[str] = None
    template: Optional[str] = None


@router.post("/generate", status_code=status.HTTP_201_CREATED)
async def generate_cover_letter(
    cover_letter_data: CoverLetterCreate,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """
    Generate AI-powered cover letter based on profile and job description
    """
    # Get user profile
    profile = await db.profiles.find_one({"user_id": user_id})
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found. Please create a profile first."
        )
    
    # Get job description
    job_description = await db.job_descriptions.find_one({
        "id": cover_letter_data.job_description_id,
        "user_id": user_id
    })
    if not job_description:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job description not found"
        )
    
    cover_letter_id = str(uuid.uuid4())
    
    # Initialize AI generator
    ai_generator = AICoverLetterGenerator()
    
    # Generate AI-powered cover letter
    print(f"Generating cover letter with {cover_letter_data.tone} tone...")
    cover_letter_content = await ai_generator.generate_cover_letter(
        profile,
        job_description,
        cover_letter_data.tone
    )
    
    # Add user's name to signature and header info
    personal_info = profile.get("personal_info", {})
    cover_letter_content["signature"] = personal_info.get("full_name", "[Your Name]")
    cover_letter_content["header"] = personal_info
    
    cover_letter_dict = {
        "id": cover_letter_id,
        "user_id": user_id,
        "profile_id": profile.get("id"),
        "job_description_id": cover_letter_data.job_description_id,
        "tone": cover_letter_data.tone,
        "template": cover_letter_data.template,
        "content": cover_letter_content,
        "status": "draft",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    await db.cover_letters.insert_one(cover_letter_dict)
    
    cover_letter_dict.pop("_id", None)
    return cover_letter_dict


@router.get("/")
async def get_cover_letters(
    skip: int = 0,
    limit: int = 20,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """
    Get all cover letters for current user with pagination
    
    Parameters:
    - skip: Number of records to skip (default: 0)
    - limit: Maximum number of records to return (default: 20, max: 100)
    """
    # Validate and cap limit
    limit = min(limit, 100)
    
    # Get total count
    total_count = await db.cover_letters.count_documents({"user_id": user_id})
    
    # Get paginated cover letters
    cursor = db.cover_letters.find({"user_id": user_id}).sort("created_at", -1).skip(skip).limit(limit)
    cover_letters = await cursor.to_list(length=limit)
    
    for letter in cover_letters:
        letter.pop("_id", None)
    
    return {
        "items": cover_letters,
        "total": total_count,
        "skip": skip,
        "limit": limit,
        "has_more": (skip + limit) < total_count
    }


@router.get("/{cover_letter_id}")
async def get_cover_letter(
    cover_letter_id: str,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """
    Get a specific cover letter
    """
    cover_letter = await db.cover_letters.find_one({"id": cover_letter_id, "user_id": user_id})
    if not cover_letter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cover letter not found"
        )
    
    cover_letter.pop("_id", None)
    return cover_letter


@router.put("/{cover_letter_id}")
async def update_cover_letter(
    cover_letter_id: str,
    update_data: CoverLetterUpdate,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """
    Update a cover letter
    """
    # Check if cover letter exists
    cover_letter = await db.cover_letters.find_one({"id": cover_letter_id, "user_id": user_id})
    if not cover_letter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cover letter not found"
        )
    
    # Build update dict
    update_dict = {"updated_at": datetime.utcnow()}
    
    if update_data.content is not None:
        update_dict["content"] = update_data.content
    if update_data.tone is not None:
        update_dict["tone"] = update_data.tone
    if update_data.template is not None:
        update_dict["template"] = update_data.template
    
    # Update cover letter
    await db.cover_letters.update_one(
        {"id": cover_letter_id, "user_id": user_id},
        {"$set": update_dict}
    )
    
    # Get updated cover letter
    updated_letter = await db.cover_letters.find_one({"id": cover_letter_id, "user_id": user_id})
    updated_letter.pop("_id", None)
    
    return updated_letter


@router.delete("/{cover_letter_id}")
async def delete_cover_letter(
    cover_letter_id: str,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """
    Delete a cover letter
    """
    result = await db.cover_letters.delete_one({"id": cover_letter_id, "user_id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cover letter not found"
        )
    
    return {"message": "Cover letter deleted successfully"}


@router.get("/templates/list")
async def get_cover_letter_templates():
    """
    Get available cover letter templates
    """
    templates = [
        {
            "id": "standard",
            "name": "Standard Professional",
            "description": "Classic business letter format, suitable for most applications"
        },
        {
            "id": "creative",
            "name": "Creative",
            "description": "Modern and engaging format for creative industries"
        },
        {
            "id": "executive",
            "name": "Executive",
            "description": "Formal and sophisticated for senior-level positions"
        }
    ]
    return templates
