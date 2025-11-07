from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from enum import Enum
import uuid

class SubscriptionTier(str, Enum):
    FREE = "free"
    PREMIUM = "premium"
    PROFESSIONAL = "professional"

class UserBase(BaseModel):
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(UserBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    is_verified: bool = False
    subscription_tier: SubscriptionTier = SubscriptionTier.FREE
    google_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "user@example.com",
                "full_name": "John Doe",
                "is_verified": True,
                "subscription_tier": "free",
                "created_at": "2024-01-01T00:00:00"
            }
        }

class UserInDB(User):
    password_hash: str

class UserResponse(UserBase):
    id: str
    is_verified: bool
    subscription_tier: SubscriptionTier
    created_at: datetime

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: Optional[str] = None
