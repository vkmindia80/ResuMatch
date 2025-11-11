"""
Admin API Routes
Manage application settings including storage configuration
"""
from fastapi import APIRouter, HTTPException, status, Depends
from models.settings import StorageSettings, StorageSettingsUpdate, AppSettings
from utils.auth import get_current_user_id, get_password_hash
from database import get_database
from datetime import datetime
import os
from dotenv import load_dotenv, set_key, find_dotenv
import uuid
from typing import Optional

load_dotenv()

router = APIRouter()


@router.get("/storage-settings")
async def get_storage_settings(
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """
    Get current storage settings
    """
    # Check if user is admin (you can add admin check logic here)
    # For now, any authenticated user can view settings
    
    # Get settings from database or use defaults
    settings_doc = await db.settings.find_one({"type": "storage"})
    
    if settings_doc:
        settings_doc.pop("_id", None)
        return settings_doc
    
    # Return default settings
    return {
        "type": "storage",
        "storage_type": os.getenv("STORAGE_TYPE", "local"),
        "local_storage_path": os.getenv("LOCAL_STORAGE_PATH", "/app/uploads"),
        "s3_bucket_name": os.getenv("S3_BUCKET_NAME"),
        "s3_region": os.getenv("S3_REGION", "us-east-1"),
        "s3_configured": bool(os.getenv("AWS_ACCESS_KEY_ID")),
        "max_file_size_mb": 10
    }


@router.put("/storage-settings")
async def update_storage_settings(
    settings: StorageSettingsUpdate,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """
    Update storage settings
    Note: Requires admin privileges in production
    """
    # In production, add admin check here
    # if not await is_admin(user_id, db):
    #     raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        # Update environment variables
        env_file = find_dotenv()
        if not env_file:
            env_file = "/app/backend/.env"
        
        update_data = settings.model_dump(exclude_unset=True)
        
        # Update .env file
        if "storage_type" in update_data:
            set_key(env_file, "STORAGE_TYPE", update_data["storage_type"])
            os.environ["STORAGE_TYPE"] = update_data["storage_type"]
        
        if "local_storage_path" in update_data:
            set_key(env_file, "LOCAL_STORAGE_PATH", update_data["local_storage_path"])
            os.environ["LOCAL_STORAGE_PATH"] = update_data["local_storage_path"]
        
        if "s3_bucket_name" in update_data:
            set_key(env_file, "S3_BUCKET_NAME", update_data["s3_bucket_name"] or "")
            os.environ["S3_BUCKET_NAME"] = update_data["s3_bucket_name"] or ""
        
        if "s3_region" in update_data:
            set_key(env_file, "S3_REGION", update_data["s3_region"])
            os.environ["S3_REGION"] = update_data["s3_region"]
        
        if "aws_access_key_id" in update_data and update_data["aws_access_key_id"]:
            set_key(env_file, "AWS_ACCESS_KEY_ID", update_data["aws_access_key_id"])
            os.environ["AWS_ACCESS_KEY_ID"] = update_data["aws_access_key_id"]
        
        if "aws_secret_access_key" in update_data and update_data["aws_secret_access_key"]:
            set_key(env_file, "AWS_SECRET_ACCESS_KEY", update_data["aws_secret_access_key"])
            os.environ["AWS_SECRET_ACCESS_KEY"] = update_data["aws_secret_access_key"]
        
        # Save to database
        settings_doc = {
            "type": "storage",
            **update_data,
            "updated_at": datetime.utcnow(),
            "updated_by": user_id
        }
        
        await db.settings.update_one(
            {"type": "storage"},
            {"$set": settings_doc},
            upsert=True
        )
        
        # Reload storage manager
        from utils.storage_manager import storage_manager
        storage_manager.__init__()  # Reinitialize with new settings
        
        return {
            "success": True,
            "message": "Storage settings updated successfully",
            "settings": settings_doc
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update settings: {str(e)}"
        )


@router.get("/storage-config")
async def get_storage_config(
    user_id: str = Depends(get_current_user_id)
):
    """
    Get current storage configuration status
    """
    from utils.storage_manager import storage_manager
    
    config = storage_manager.get_storage_config()
    
    return {
        "success": True,
        "config": config
    }
