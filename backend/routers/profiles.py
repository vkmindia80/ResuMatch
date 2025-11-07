from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File
from models.profile import Profile, ProfileUpdate, PersonalInfo
from utils.auth import get_current_user_id
from utils.profile_analyzer import calculate_completeness_score, get_missing_sections
from utils.resume_parser import ResumeParser
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

@router.post("/parse-resume")
async def parse_resume(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """
    Parse resume and auto-fill profile
    Supports PDF, DOCX, and TXT files
    """
    # Validate file type
    allowed_extensions = ['pdf', 'docx', 'doc', 'txt']
    file_extension = file.filename.lower().split('.')[-1]
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not supported. Allowed types: {', '.join(allowed_extensions)}"
        )
    
    # Validate file size (max 10MB)
    file_content = await file.read()
    if len(file_content) > 10 * 1024 * 1024:  # 10MB
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size too large. Maximum size is 10MB."
        )
    
    try:
        # Parse resume using AI
        parser = ResumeParser()
        result = await parser.parse_resume(file_content, file.filename)
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to parse resume: {result['error']}"
            )
        
        parsed_data = result["data"]
        
        # Check if profile exists
        existing_profile = await db.profiles.find_one({"user_id": user_id})
        
        if existing_profile:
            # Update existing profile with parsed data
            update_data = {
                "personal_info": parsed_data.get("personal_info", {}),
                "education": parsed_data.get("education", []),
                "experience": parsed_data.get("experience", []),
                "skills": parsed_data.get("skills", {}),
                "projects": parsed_data.get("projects", []),
                "certifications": parsed_data.get("certifications", []),
                "updated_at": datetime.utcnow()
            }
            
            # Update profile
            await db.profiles.update_one(
                {"user_id": user_id},
                {"$set": update_data}
            )
            
            # Recalculate completeness score
            updated_profile = await db.profiles.find_one({"user_id": user_id})
            profile_obj = Profile(**updated_profile)
            new_score = calculate_completeness_score(profile_obj)
            
            await db.profiles.update_one(
                {"user_id": user_id},
                {"$set": {"completeness_score": new_score}}
            )
            
            message = "Profile updated successfully from resume"
        else:
            # Create new profile with parsed data
            profile_data = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "personal_info": parsed_data.get("personal_info", {}),
                "education": parsed_data.get("education", []),
                "experience": parsed_data.get("experience", []),
                "skills": parsed_data.get("skills", {}),
                "projects": parsed_data.get("projects", []),
                "certifications": parsed_data.get("certifications", []),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Calculate completeness score
            profile_obj = Profile(**profile_data)
            profile_data["completeness_score"] = calculate_completeness_score(profile_obj)
            
            await db.profiles.insert_one(profile_data)
            message = "Profile created successfully from resume"
        
        # Get final profile
        final_profile = await db.profiles.find_one({"user_id": user_id})
        final_profile.pop("_id", None)
        
        return {
            "success": True,
            "message": message,
            "profile": final_profile,
            "raw_text_preview": result.get("raw_text", "")
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while parsing the resume: {str(e)}"
        )
