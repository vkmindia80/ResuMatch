from fastapi import APIRouter, HTTPException, status, Depends
from utils.auth import get_current_user_id
from server import get_database

router = APIRouter()

@router.get("/me")
async def get_user_profile(user_id: str = Depends(get_current_user_id), db = Depends(get_database)):
    """
    Get current user information
    """
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Remove sensitive data
    user.pop("password_hash", None)
    user.pop("_id", None)
    
    return user

@router.delete("/me")
async def delete_user_account(user_id: str = Depends(get_current_user_id), db = Depends(get_database)):
    """
    Delete user account and all associated data
    """
    # Delete user data from all collections
    await db.users.delete_one({"id": user_id})
    await db.profiles.delete_one({"user_id": user_id})
    await db.job_descriptions.delete_many({"user_id": user_id})
    await db.resumes.delete_many({"user_id": user_id})
    await db.interview_questions.delete_many({"user_id": user_id})
    
    return {"message": "Account successfully deleted"}
