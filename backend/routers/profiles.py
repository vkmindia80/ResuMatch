from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File
from models.profile import Profile, ProfileUpdate, PersonalInfo
from utils.auth import get_current_user_id
from utils.profile_analyzer import calculate_completeness_score, get_missing_sections
from utils.resume_parser import ResumeParser
from database import get_database
from datetime import datetime, date
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
    
    try:
        # Build update dict
        update_data = profile_update.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No data to update"
            )
        
        # Convert date objects to ISO format strings for MongoDB
        def convert_dates_to_strings(data):
            """Recursively convert date objects to ISO strings"""
            if isinstance(data, dict):
                return {k: convert_dates_to_strings(v) for k, v in data.items()}
            elif isinstance(data, list):
                return [convert_dates_to_strings(item) for item in data]
            elif isinstance(data, date):
                return data.isoformat()
            return data
        
        update_data = convert_dates_to_strings(update_data)
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
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Error updating profile: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile: {str(e)}"
        )

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
        
        # Transform parsed data to match Profile model format
        # Convert date strings to date objects and handle nested structures
        from datetime import datetime
        
        def parse_date_string(date_str):
            """Parse date string in various formats"""
            if not date_str or date_str == "":
                return None
            try:
                # Try YYYY-MM-DD format
                return datetime.strptime(date_str, "%Y-%m-%d").date()
            except:
                try:
                    # Try YYYY-MM format
                    return datetime.strptime(date_str + "-01", "%Y-%m-%d").date()
                except:
                    try:
                        # Try YYYY format
                        return datetime.strptime(date_str + "-01-01", "%Y-%m-%d").date()
                    except:
                        return None
        
        # Transform education dates (keep as strings for MongoDB)
        for edu in parsed_data.get("education", []):
            if "start_date" in edu:
                if edu["start_date"] and edu["start_date"] != "":
                    date_obj = parse_date_string(edu["start_date"])
                    edu["start_date"] = date_obj.isoformat() if date_obj else None
                else:
                    edu["start_date"] = None
            if "end_date" in edu:
                if edu["end_date"] and edu["end_date"] != "":
                    date_obj = parse_date_string(edu["end_date"])
                    edu["end_date"] = date_obj.isoformat() if date_obj else None
                else:
                    edu["end_date"] = None
            # Handle GPA format (e.g., "3.8/4.0" -> 3.8)
            if "gpa" in edu and edu["gpa"]:
                gpa_str = str(edu["gpa"])
                if "/" in gpa_str:
                    try:
                        edu["gpa"] = float(gpa_str.split("/")[0])
                    except:
                        edu["gpa"] = None
                else:
                    try:
                        edu["gpa"] = float(gpa_str)
                    except:
                        edu["gpa"] = None
        
        # Transform experience dates (keep as strings for MongoDB)
        for exp in parsed_data.get("experience", []):
            if "start_date" in exp:
                if exp["start_date"] and exp["start_date"] != "":
                    date_obj = parse_date_string(exp["start_date"])
                    exp["start_date"] = date_obj.isoformat() if date_obj else None
                else:
                    exp["start_date"] = None
            if "end_date" in exp:
                if exp["end_date"] and exp["end_date"] != "":
                    date_obj = parse_date_string(exp["end_date"])
                    exp["end_date"] = date_obj.isoformat() if date_obj else None
                else:
                    exp["end_date"] = None
        
        # Transform skills to proper format
        skills_data = parsed_data.get("skills", {})
        transformed_skills = {
            "technical": [],
            "soft": skills_data.get("soft", []),
            "languages": [],
            "tools": skills_data.get("tools", [])
        }
        
        # Convert technical skills to Skill objects
        for skill in skills_data.get("technical", []):
            if isinstance(skill, str):
                transformed_skills["technical"].append({"name": skill, "level": None})
            else:
                transformed_skills["technical"].append(skill)
        
        # Convert languages to Language objects
        for lang in skills_data.get("languages", []):
            if isinstance(lang, str):
                # Try to extract fluency level from string like "English (Native)"
                if "(" in lang and ")" in lang:
                    name = lang.split("(")[0].strip()
                    fluency = lang.split("(")[1].replace(")", "").strip()
                else:
                    name = lang
                    fluency = "Unknown"
                transformed_skills["languages"].append({"name": name, "fluency": fluency})
            else:
                transformed_skills["languages"].append(lang)
        
        parsed_data["skills"] = transformed_skills
        
        # Transform projects dates (keep as strings for MongoDB)
        for proj in parsed_data.get("projects", []):
            if "start_date" in proj:
                if proj["start_date"] and proj["start_date"] != "":
                    date_obj = parse_date_string(proj["start_date"])
                    proj["start_date"] = date_obj.isoformat() if date_obj else None
                else:
                    proj["start_date"] = None
            if "end_date" in proj:
                if proj["end_date"] and proj["end_date"] != "":
                    date_obj = parse_date_string(proj["end_date"])
                    proj["end_date"] = date_obj.isoformat() if date_obj else None
                else:
                    proj["end_date"] = None
        
        # Transform certifications dates (keep as strings for MongoDB)
        for cert in parsed_data.get("certifications", []):
            if "issue_date" in cert:
                if cert["issue_date"] and cert["issue_date"] != "":
                    date_obj = parse_date_string(cert["issue_date"])
                    cert["issue_date"] = date_obj.isoformat() if date_obj else None
                else:
                    cert["issue_date"] = None
            if "expiry_date" in cert:
                if cert["expiry_date"] and cert["expiry_date"] != "":
                    date_obj = parse_date_string(cert["expiry_date"])
                    cert["expiry_date"] = date_obj.isoformat() if date_obj else None
                else:
                    cert["expiry_date"] = None
        
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


@router.post("/suggest-achievements")
async def suggest_achievements(
    job_title: str,
    company: str,
    responsibilities: list[str] = [],
    technologies: list[str] = [],
    user_id: str = Depends(get_current_user_id)
):
    """
    Generate AI-powered achievement suggestions for work experience
    """
    try:
        from utils.ai_suggestions import ai_suggestion_engine
        
        suggestions = await ai_suggestion_engine.suggest_achievements(
            job_title=job_title,
            company=company,
            responsibilities=responsibilities,
            technologies=technologies
        )
        
        return {
            "success": True,
            "suggestions": suggestions
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate suggestions: {str(e)}"
        )


@router.post("/suggest-skills")
async def suggest_skills(
    job_title: str = None,
    industry: str = None,
    current_skills: list[str] = [],
    experience_level: str = "Intermediate",
    user_id: str = Depends(get_current_user_id)
):
    """
    Generate AI-powered skill suggestions categorized as technical and soft skills
    """
    try:
        from utils.ai_suggestions import ai_suggestion_engine
        
        suggestions = await ai_suggestion_engine.suggest_skills(
            job_title=job_title,
            industry=industry,
            current_skills=current_skills,
            experience_level=experience_level
        )
        
        return {
            "success": True,
            "suggestions": suggestions
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate skill suggestions: {str(e)}"
        )


@router.post("/categorize-skills")
async def categorize_skills(
    skills: list[str],
    user_id: str = Depends(get_current_user_id)
):
    """
    Categorize skills into technical and soft skills using AI
    """
    try:
        from utils.ai_suggestions import ai_suggestion_engine
        
        categorized = await ai_suggestion_engine.categorize_skills(skills=skills)
        
        return {
            "success": True,
            "categorized": categorized
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to categorize skills: {str(e)}"
        )


@router.post("/suggest-responsibilities")
async def suggest_responsibilities(
    job_title: str,
    company: str,
    current_responsibilities: list[str] = [],
    technologies: list[str] = [],
    job_description: str = None,
    user_id: str = Depends(get_current_user_id)
):
    """
    Generate AI-powered responsibility suggestions for work experience
    """
    try:
        from utils.ai_suggestions import ai_suggestion_engine
        
        suggestions = await ai_suggestion_engine.suggest_responsibilities(
            job_title=job_title,
            company=company,
            current_responsibilities=current_responsibilities,
            technologies=technologies,
            job_description=job_description
        )
        
        return {
            "success": True,
            "suggestions": suggestions
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate responsibility suggestions: {str(e)}"
        )


@router.post("/suggest-technologies")
async def suggest_technologies(
    job_title: str,
    company: str = None,
    current_technologies: list[str] = [],
    industry: str = None,
    job_description: str = None,
    user_id: str = Depends(get_current_user_id)
):
    """
    Generate AI-powered technology/tool suggestions based on role, industry, and job description
    """
    try:
        from utils.ai_suggestions import ai_suggestion_engine
        
        suggestions = await ai_suggestion_engine.suggest_technologies(
            job_title=job_title,
            company=company,
            current_technologies=current_technologies,
            industry=industry,
            job_description=job_description
        )
        
        return {
            "success": True,
            "suggestions": suggestions
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate technology suggestions: {str(e)}"
        )


@router.post("/upload-certificate")
async def upload_certificate(
    file: UploadFile = File(...),
    education_id: str = None,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """
    Upload education certificate
    Supports PDF, JPG, PNG files
    """
    # Validate file type
    allowed_extensions = ['pdf', 'jpg', 'jpeg', 'png']
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
        from utils.storage_manager import storage_manager
        
        # Determine content type
        content_type_map = {
            'pdf': 'application/pdf',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png'
        }
        content_type = content_type_map.get(file_extension, 'application/octet-stream')
        
        # Upload file
        storage_info = await storage_manager.upload_file(
            file_content=file_content,
            filename=file.filename,
            folder="certificates",
            content_type=content_type
        )
        
        # If education_id is provided, update the education record
        if education_id:
            profile = await db.profiles.find_one({"user_id": user_id})
            if profile:
                # Update specific education entry
                education_list = profile.get("education", [])
                for edu in education_list:
                    if edu.get("id") == education_id:
                        edu["certificate_url"] = storage_info["url"]
                        edu["certificate_storage_info"] = storage_info
                        break
                
                await db.profiles.update_one(
                    {"user_id": user_id},
                    {"$set": {"education": education_list, "updated_at": datetime.utcnow()}}
                )
        
        return {
            "success": True,
            "message": "Certificate uploaded successfully",
            "storage_info": storage_info
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload certificate: {str(e)}"
        )


@router.delete("/delete-certificate/{education_id}")
async def delete_certificate(
    education_id: str,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """
    Delete education certificate
    """
    try:
        from utils.storage_manager import storage_manager
        
        profile = await db.profiles.find_one({"user_id": user_id})
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        
        # Find education entry
        education_list = profile.get("education", [])
        education_entry = None
        for edu in education_list:
            if edu.get("id") == education_id:
                education_entry = edu
                break
        
        if not education_entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Education entry not found"
            )
        
        # Delete from storage if exists
        if education_entry.get("certificate_storage_info"):
            await storage_manager.delete_file(education_entry["certificate_storage_info"])
        
        # Update database
        education_entry["certificate_url"] = None
        education_entry["certificate_storage_info"] = None
        
        await db.profiles.update_one(
            {"user_id": user_id},
            {"$set": {"education": education_list, "updated_at": datetime.utcnow()}}
        )
        
        return {
            "success": True,
            "message": "Certificate deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete certificate: {str(e)}"
        )
