from fastapi import APIRouter, HTTPException, status, Depends, WebSocket, WebSocketDisconnect
from typing import List, Optional
from datetime import datetime, timedelta
from utils.auth import get_current_user_id
from utils.live_interview_ai import LiveInterviewAI
from database import get_database
from models.live_interview import (
    StartSessionRequest,
    TranscriptRequest,
    GenerateAnswerRequest,
    SessionStatus,
    TranscriptEntry,
    AIAnswer
)
import uuid
import json

router = APIRouter()

# Store active WebSocket connections
active_connections: dict = {}

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket
    
    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
    
    async def send_message(self, session_id: str, message: dict):
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_json(message)

manager = ConnectionManager()

@router.post("/sessions/start", status_code=status.HTTP_201_CREATED)
async def start_live_session(
    request: StartSessionRequest,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Start a new live interview session"""
    
    # Verify job description if provided
    if request.job_description_id:
        job = await db.job_descriptions.find_one({
            "id": request.job_description_id,
            "user_id": user_id
        })
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job description not found"
            )
    
    # Verify resume if provided
    if request.resume_id:
        resume = await db.resumes.find_one({
            "id": request.resume_id,
            "user_id": user_id
        })
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found"
            )
    
    # Create session
    session_id = str(uuid.uuid4())
    session = {
        "id": session_id,
        "user_id": user_id,
        "job_description_id": request.job_description_id,
        "resume_id": request.resume_id,
        "resume_source": request.resume_source,
        "title": request.title,
        "status": SessionStatus.ACTIVE.value,
        "started_at": datetime.utcnow(),
        "ended_at": None,
        "duration_seconds": 0,
        "language": request.language,
        "model_preference": request.model_preference,
        "created_at": datetime.utcnow()
    }
    
    await db.live_interview_sessions.insert_one(session)
    
    # Create transcript document
    transcript = {
        "id": str(uuid.uuid4()),
        "session_id": session_id,
        "user_id": user_id,
        "entries": [],
        "ai_answers": [],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    await db.interview_transcripts.insert_one(transcript)
    
    session.pop("_id", None)
    return session

@router.post("/sessions/{session_id}/transcript")
async def add_transcript_entry(
    session_id: str,
    request: TranscriptRequest,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Add a transcript entry to the session"""
    
    # Verify session
    session = await db.live_interview_sessions.find_one({
        "id": session_id,
        "user_id": user_id
    })
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Create transcript entry
    entry = {
        "timestamp": datetime.utcnow(),
        "text": request.text,
        "type": request.type,
        "confidence": request.confidence
    }
    
    # Update transcript
    await db.interview_transcripts.update_one(
        {"session_id": session_id},
        {
            "$push": {"entries": entry},
            "$set": {"updated_at": datetime.utcnow()}
        }
    )
    
    return {"status": "success", "entry": entry}

@router.post("/sessions/{session_id}/generate-answer")
async def generate_ai_answer(
    session_id: str,
    request: GenerateAnswerRequest,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Generate AI answer for a question"""
    
    # Verify session
    session = await db.live_interview_sessions.find_one({
        "id": session_id,
        "user_id": user_id
    })
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Get user profile
    profile = await db.profiles.find_one({"user_id": user_id})
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found. Please complete your profile first."
        )
    
    # Get job description if available
    job_description = None
    if session.get("job_description_id"):
        job_description = await db.job_descriptions.find_one({
            "id": session["job_description_id"]
        })
    
    # Generate AI answer
    ai = LiveInterviewAI()
    answer_data = await ai.generate_instant_answer(
        question=request.question,
        user_profile=profile,
        job_description=job_description,
        model=session.get("model_preference", "gpt-4")
    )
    
    # Store answer in transcript
    await db.interview_transcripts.update_one(
        {"session_id": session_id},
        {
            "$push": {"ai_answers": answer_data},
            "$set": {"updated_at": datetime.utcnow()}
        }
    )
    
    return answer_data

@router.put("/sessions/{session_id}/status")
async def update_session_status(
    session_id: str,
    status_update: dict,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Update session status (pause, resume, complete)"""
    
    new_status = status_update.get("status")
    if new_status not in [s.value for s in SessionStatus]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid status"
        )
    
    update_data = {"status": new_status}
    
    # If completing, calculate duration
    if new_status == SessionStatus.COMPLETED.value:
        session = await db.live_interview_sessions.find_one({"id": session_id})
        if session:
            started_at = session["started_at"]
            duration = (datetime.utcnow() - started_at).total_seconds()
            update_data["ended_at"] = datetime.utcnow()
            update_data["duration_seconds"] = int(duration)
    
    result = await db.live_interview_sessions.update_one(
        {"id": session_id, "user_id": user_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    return {"status": "success", "new_status": new_status}

@router.get("/sessions")
async def get_sessions(
    skip: int = 0,
    limit: int = 20,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Get user's interview sessions"""
    
    cursor = db.live_interview_sessions.find(
        {"user_id": user_id}
    ).sort("started_at", -1).skip(skip).limit(limit)
    
    sessions = await cursor.to_list(length=limit)
    total = await db.live_interview_sessions.count_documents({"user_id": user_id})
    
    for session in sessions:
        session.pop("_id", None)
    
    return {
        "items": sessions,
        "total": total,
        "skip": skip,
        "limit": limit
    }

@router.get("/sessions/{session_id}")
async def get_session(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Get session details"""
    
    session = await db.live_interview_sessions.find_one({
        "id": session_id,
        "user_id": user_id
    })
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    session.pop("_id", None)
    return session

@router.get("/sessions/{session_id}/transcript")
async def get_session_transcript(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Get session transcript"""
    
    # Verify session belongs to user
    session = await db.live_interview_sessions.find_one({
        "id": session_id,
        "user_id": user_id
    })
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    transcript = await db.interview_transcripts.find_one({"session_id": session_id})
    
    if not transcript:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transcript not found"
        )
    
    transcript.pop("_id", None)
    return transcript

@router.post("/sessions/{session_id}/analyze")
async def analyze_session(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Generate AI analysis of interview performance"""
    
    # Verify session
    session = await db.live_interview_sessions.find_one({
        "id": session_id,
        "user_id": user_id
    })
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Get transcript
    transcript = await db.interview_transcripts.find_one({"session_id": session_id})
    if not transcript:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transcript not found"
        )
    
    # Get user profile
    profile = await db.profiles.find_one({"user_id": user_id})
    
    # Generate analysis
    ai = LiveInterviewAI()
    analysis_data = await ai.analyze_interview_performance(
        transcript_entries=transcript.get("entries", []),
        ai_answers=transcript.get("ai_answers", []),
        user_profile=profile or {}
    )
    
    # Store analysis
    analysis = {
        "id": str(uuid.uuid4()),
        "session_id": session_id,
        "user_id": user_id,
        "created_at": datetime.utcnow(),
        **analysis_data
    }
    
    # Check if analysis already exists
    existing = await db.interview_analysis.find_one({"session_id": session_id})
    if existing:
        await db.interview_analysis.update_one(
            {"session_id": session_id},
            {"$set": analysis}
        )
    else:
        await db.interview_analysis.insert_one(analysis)
    
    analysis.pop("_id", None)
    return analysis

@router.get("/sessions/{session_id}/analysis")
async def get_session_analysis(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Get session analysis"""
    
    # Verify session belongs to user
    session = await db.live_interview_sessions.find_one({
        "id": session_id,
        "user_id": user_id
    })
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    analysis = await db.interview_analysis.find_one({"session_id": session_id})
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found. Generate analysis first."
        )
    
    analysis.pop("_id", None)
    return analysis

@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Delete a session and its related data"""
    
    # Delete session
    result = await db.live_interview_sessions.delete_one({
        "id": session_id,
        "user_id": user_id
    })
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Delete transcript and analysis
    await db.interview_transcripts.delete_one({"session_id": session_id})
    await db.interview_analysis.delete_one({"session_id": session_id})
    
    return {"status": "success", "message": "Session deleted"}
