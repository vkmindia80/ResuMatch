from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class SessionStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class TranscriptEntry(BaseModel):
    timestamp: datetime
    text: str
    type: str  # "question" or "user_speech"
    confidence: Optional[float] = None

class AIAnswer(BaseModel):
    question: str
    answer: str
    context_used: List[str]  # Which parts of profile/resume were used
    generated_at: datetime
    model: str  # "gpt-4" or "claude-sonnet"

class LiveInterviewSession(BaseModel):
    id: str
    user_id: str
    job_description_id: Optional[str] = None
    title: str
    status: SessionStatus = SessionStatus.ACTIVE
    started_at: datetime
    ended_at: Optional[datetime] = None
    duration_seconds: int = 0
    language: str = "en-US"
    model_preference: str = "gpt-4"  # or "claude-sonnet"
    
class InterviewTranscript(BaseModel):
    id: str
    session_id: str
    user_id: str
    entries: List[TranscriptEntry] = []
    ai_answers: List[AIAnswer] = []
    created_at: datetime
    updated_at: datetime

class InterviewAnalysis(BaseModel):
    id: str
    session_id: str
    user_id: str
    overall_score: float  # 0-100
    communication_score: float
    technical_score: float
    behavioral_score: float
    strengths: List[str]
    areas_for_improvement: List[str]
    detailed_feedback: str
    question_count: int
    answer_quality_avg: float
    created_at: datetime

class StartSessionRequest(BaseModel):
    title: str
    job_description_id: Optional[str] = None
    language: str = "en-US"
    model_preference: str = "gpt-4"

class TranscriptRequest(BaseModel):
    text: str
    type: str  # "question" or "user_speech"
    confidence: Optional[float] = None

class GenerateAnswerRequest(BaseModel):
    question: str
    session_id: str
