from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime, date
import uuid

class PersonalInfo(BaseModel):
    full_name: str
    email: str
    phone: Optional[str] = None
    location: Optional[str] = None
    title: Optional[str] = None
    linkedin: Optional[str] = None
    portfolio: Optional[str] = None
    photo_url: Optional[str] = None

class Education(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    institution: str
    degree: str
    field: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    gpa: Optional[float] = None
    achievements: List[str] = []
    certificate_url: Optional[str] = None
    certificate_storage_info: Optional[Dict] = None

class Experience(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    company: str
    title: str
    employment_type: str = "Full-time"
    start_date: date
    end_date: Optional[date] = None
    is_current: bool = False
    location: Optional[str] = None
    responsibilities: List[str] = []
    achievements: List[str] = []
    technologies: List[str] = []

class Skill(BaseModel):
    name: str
    level: Optional[str] = None  # Beginner, Intermediate, Advanced, Expert

class Language(BaseModel):
    name: str
    fluency: str  # Native, Fluent, Intermediate, Basic

class Skills(BaseModel):
    technical: List[Skill] = []
    soft: List[str] = []
    languages: List[Language] = []
    tools: List[str] = []

class Project(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    technologies: List[str] = []
    role: Optional[str] = None
    url: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class Certification(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    issuer: str
    issue_date: date
    expiry_date: Optional[date] = None
    credential_id: Optional[str] = None

class Profile(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    personal_info: PersonalInfo
    education: List[Education] = []
    experience: List[Experience] = []
    skills: Skills = Skills()
    projects: List[Project] = []
    certifications: List[Certification] = []
    completeness_score: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "123e4567-e89b-12d3-a456-426614174001",
                "personal_info": {
                    "full_name": "John Doe",
                    "email": "john@example.com",
                    "phone": "+1234567890",
                    "location": "San Francisco, CA",
                    "title": "Software Engineer"
                },
                "completeness_score": 75
            }
        }

class ProfileUpdate(BaseModel):
    personal_info: Optional[PersonalInfo] = None
    education: Optional[List[Education]] = None
    experience: Optional[List[Experience]] = None
    skills: Optional[Skills] = None
    projects: Optional[List[Project]] = None
    certifications: Optional[List[Certification]] = None
