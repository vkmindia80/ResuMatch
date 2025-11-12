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


# AI Configuration Models

class AIProviderConfig(BaseModel):
    """Configuration for an AI provider"""
    enabled: bool = False
    api_key: Optional[str] = None
    default_model: Optional[str] = None
    # Provider-specific settings
    organization_id: Optional[str] = None  # For OpenAI
    project_id: Optional[str] = None  # For Google


class FeatureAIConfig(BaseModel):
    """AI configuration for a specific feature"""
    provider: Literal["emergent", "openai", "anthropic", "google", "custom"] = "emergent"
    model: Optional[str] = None
    use_custom_key: bool = False


class AISettings(BaseModel):
    """AI configuration settings"""
    # Global settings
    use_emergent_key: bool = True
    emergent_key_enabled: bool = True
    
    # Provider configurations
    openai: AIProviderConfig = AIProviderConfig()
    anthropic: AIProviderConfig = AIProviderConfig()
    google: AIProviderConfig = AIProviderConfig()
    custom: AIProviderConfig = AIProviderConfig()
    
    # Per-feature configurations
    resume_generation: FeatureAIConfig = FeatureAIConfig(provider="emergent", model="gpt-4o")
    interview_prep: FeatureAIConfig = FeatureAIConfig(provider="emergent", model="gpt-4o")
    cover_letter: FeatureAIConfig = FeatureAIConfig(provider="emergent", model="gpt-4o")
    live_interview: FeatureAIConfig = FeatureAIConfig(provider="emergent", model="gpt-4o")
    ats_optimization: FeatureAIConfig = FeatureAIConfig(provider="emergent", model="gpt-4o")


class AISettingsUpdate(BaseModel):
    """Update AI settings"""
    use_emergent_key: Optional[bool] = None
    
    # Provider configurations
    openai: Optional[AIProviderConfig] = None
    anthropic: Optional[AIProviderConfig] = None
    google: Optional[AIProviderConfig] = None
    custom: Optional[AIProviderConfig] = None
    
    # Per-feature configurations
    resume_generation: Optional[FeatureAIConfig] = None
    interview_prep: Optional[FeatureAIConfig] = None
    cover_letter: Optional[FeatureAIConfig] = None
    live_interview: Optional[FeatureAIConfig] = None
    ats_optimization: Optional[FeatureAIConfig] = None


class UserAISettings(BaseModel):
    """User-specific AI configuration (overrides admin defaults)"""
    user_id: str
    
    # Override admin settings
    use_custom_keys: bool = False
    
    # Provider configurations
    openai: Optional[AIProviderConfig] = None
    anthropic: Optional[AIProviderConfig] = None
    google: Optional[AIProviderConfig] = None
    custom: Optional[AIProviderConfig] = None
    
    # Per-feature configurations
    resume_generation: Optional[FeatureAIConfig] = None
    interview_prep: Optional[FeatureAIConfig] = None
    cover_letter: Optional[FeatureAIConfig] = None
    live_interview: Optional[FeatureAIConfig] = None
    ats_optimization: Optional[FeatureAIConfig] = None
    
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()


class UserAISettingsUpdate(BaseModel):
    """Update user AI settings"""
    use_custom_keys: Optional[bool] = None
    
    openai: Optional[AIProviderConfig] = None
    anthropic: Optional[AIProviderConfig] = None
    google: Optional[AIProviderConfig] = None
    custom: Optional[AIProviderConfig] = None
    
    resume_generation: Optional[FeatureAIConfig] = None
    interview_prep: Optional[FeatureAIConfig] = None
    cover_letter: Optional[FeatureAIConfig] = None
    live_interview: Optional[FeatureAIConfig] = None
    ats_optimization: Optional[FeatureAIConfig] = None
