from fastapi import APIRouter, HTTPException, status, Depends
from models.profile import Profile, ProfileUpdate, PersonalInfo
from utils.auth import get_current_user_id
from utils.profile_analyzer import calculate_completeness_score, get_missing_sections
from database import get_database
from datetime import datetime
import uuid

router = APIRouter()

@router.get("/me")
async def get_profile(user_id: str = Depends(get_current_user_id), db = Depends(get_database)):
    """
    Get user profile
    """
    profile = await db.profiles.find_one({"user_id": user_id})
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found. Please create a profile first."
        )
    
    profile.pop("_id", None)
    return profile

@router.post("/me", status_code=status.HTTP_201_CREATED)
async def create_profile(
    personal_info: PersonalInfo,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """
    Create user profile
    """
    # Check if profile already exists
    existing_profile = await db.profiles.find_one({"user_id": user_id})
    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile already exists"
        )
    
    profile = Profile(
        user_id=user_id,
        personal_info=personal_info
    )
    
    # Calculate completeness score
    profile.completeness_score = calculate_completeness_score(profile)
    
    profile_dict = profile.model_dump()
    await db.profiles.insert_one(profile_dict)
    
    profile_dict.pop("_id", None)
    return profile_dict

@router.put("/me")
async def update_profile(
    profile_update: ProfileUpdate,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """
    Update user profile
    """
    existing_profile = await db.profiles.find_one({"user_id": user_id})
    if not existing_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    # Build update dict
    update_data = profile_update.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No data to update"
        )
    
    update_data["updated_at"] = datetime.utcnow()
    
    # Update profile
    await db.profiles.update_one(
        {"user_id": user_id},
        {"$set": update_data}
    )
    
    # Get updated profile and recalculate score
    updated_profile = await db.profiles.find_one({"user_id": user_id})
    profile_obj = Profile(**updated_profile)
    new_score = calculate_completeness_score(profile_obj)
    
    await db.profiles.update_one(
        {"user_id": user_id},
        {"$set": {"completeness_score": new_score}}
    )
    
    updated_profile = await db.profiles.find_one({"user_id": user_id})
    updated_profile.pop("_id", None)
    
    return updated_profile

@router.get("/completeness")
async def get_profile_completeness(user_id: str = Depends(get_current_user_id), db = Depends(get_database)):
    """
    Get profile completeness score and missing sections
    """
    profile = await db.profiles.find_one({"user_id": user_id})
    if not profile:
        return {
            "score": 0,
            "missing_sections": {"profile": "Profile not created yet"}
        }
    
    profile_obj = Profile(**profile)
    score = calculate_completeness_score(profile_obj)
    missing = get_missing_sections(profile_obj)
    
    return {
        "score": score,
        "missing_sections": missing
    }
