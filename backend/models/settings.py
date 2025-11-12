"""
Application Settings Models
"""
from pydantic import BaseModel
from typing import Optional, Literal, Dict
from datetime import datetime
import uuid


class StorageSettings(BaseModel):
    """Storage configuration settings"""
    storage_type: Literal["local", "s3", "database"] = "local"
    
    # Local storage settings
    local_storage_path: Optional[str] = "/app/uploads"
    
    # S3 settings
    s3_bucket_name: Optional[str] = None
    s3_region: Optional[str] = "us-east-1"
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    
    # Database storage settings
    max_file_size_mb: int = 10


class AppSettings(BaseModel):
    """Application-wide settings"""
    id: str = uuid.uuid4().hex
    storage: StorageSettings = StorageSettings()
    updated_at: datetime = datetime.utcnow()
    updated_by: Optional[str] = None


class StorageSettingsUpdate(BaseModel):
    """Update storage settings"""
    storage_type: Optional[Literal["local", "s3", "database"]] = None
    local_storage_path: Optional[str] = None
    s3_bucket_name: Optional[str] = None
    s3_region: Optional[str] = None
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    max_file_size_mb: Optional[int] = None
