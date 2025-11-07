from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from utils.auth import get_current_user_id
from database import get_database
from datetime import datetime, timedelta
import uuid

router = APIRouter()


class PracticeSessionCreate(BaseModel):
    job_description_id: str
    question_ids: List[str]
    duration_seconds: Optional[int] = 0
    notes: Optional[str] = ""


class PracticeSessionUpdate(BaseModel):
    duration_seconds: Optional[int] = None
    notes: Optional[str] = None
    completed: Optional[bool] = None
    answers_given: Optional[Dict[str, str]] = None


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_practice_session(
    session_data: PracticeSessionCreate,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """
    Create a new practice session
    """
    # Verify job description exists
    job_description = await db.job_descriptions.find_one({
        "id": session_data.job_description_id,
        "user_id": user_id
    })
    if not job_description:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job description not found"
        )
    
    # Verify questions exist
    questions_cursor = db.interview_questions.find({
        "id": {"$in": session_data.question_ids},
        "user_id": user_id
    })
    questions = await questions_cursor.to_list(length=len(session_data.question_ids))
    
    if len(questions) != len(session_data.question_ids):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or more questions not found"
        )
    
    session_id = str(uuid.uuid4())
    
    session_dict = {
        "id": session_id,
        "user_id": user_id,
        "job_description_id": session_data.job_description_id,
        "question_ids": session_data.question_ids,
        "questions_count": len(session_data.question_ids),
        "duration_seconds": session_data.duration_seconds,
        "notes": session_data.notes,
        "answers_given": {},
        "completed": False,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "completed_at": None
    }
    
    await db.practice_sessions.insert_one(session_dict)
    
    # Update practice count for questions
    await db.interview_questions.update_many(
        {"id": {"$in": session_data.question_ids}, "user_id": user_id},
        {
            "$inc": {"practice_count": 1},
            "$set": {"last_practiced": datetime.utcnow()}
        }
    )
    
    session_dict.pop("_id", None)
    return session_dict


@router.get("/")
async def get_practice_sessions(
    skip: int = 0,
    limit: int = 20,
    job_description_id: Optional[str] = None,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """
    Get all practice sessions for current user with pagination
    
    Parameters:
    - skip: Number of records to skip (default: 0)
    - limit: Maximum number of records to return (default: 20, max: 100)
    - job_description_id: Filter by job description (optional)
    """
    # Validate and cap limit
    limit = min(limit, 100)
    
    # Build query
    query = {"user_id": user_id}
    if job_description_id:
        query["job_description_id"] = job_description_id
    
    # Get total count
    total_count = await db.practice_sessions.count_documents(query)
    
    # Get paginated sessions
    cursor = db.practice_sessions.find(query).sort("created_at", -1).skip(skip).limit(limit)
    sessions = await cursor.to_list(length=limit)
    
    for session in sessions:
        session.pop("_id", None)
    
    return {
        "items": sessions,
        "total": total_count,
        "skip": skip,
        "limit": limit,
        "has_more": (skip + limit) < total_count
    }


@router.get("/{session_id}")
async def get_practice_session(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """
    Get a specific practice session
    """
    session = await db.practice_sessions.find_one({"id": session_id, "user_id": user_id})
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Practice session not found"
        )
    
    session.pop("_id", None)
    return session


@router.put("/{session_id}")
async def update_practice_session(
    session_id: str,
    update_data: PracticeSessionUpdate,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """
    Update a practice session
    """
    # Check if session exists
    session = await db.practice_sessions.find_one({"id": session_id, "user_id": user_id})
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Practice session not found"
        )
    
    # Build update dict
    update_dict = {"updated_at": datetime.utcnow()}
    
    if update_data.duration_seconds is not None:
        update_dict["duration_seconds"] = update_data.duration_seconds
    if update_data.notes is not None:
        update_dict["notes"] = update_data.notes
    if update_data.answers_given is not None:
        update_dict["answers_given"] = update_data.answers_given
    if update_data.completed is not None:
        update_dict["completed"] = update_data.completed
        if update_data.completed:
            update_dict["completed_at"] = datetime.utcnow()
    
    # Update session
    await db.practice_sessions.update_one(
        {"id": session_id, "user_id": user_id},
        {"$set": update_dict}
    )
    
    # Get updated session
    updated_session = await db.practice_sessions.find_one({"id": session_id, "user_id": user_id})
    updated_session.pop("_id", None)
    
    return updated_session


@router.delete("/{session_id}")
async def delete_practice_session(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """
    Delete a practice session
    """
    result = await db.practice_sessions.delete_one({"id": session_id, "user_id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Practice session not found"
        )
    
    return {"message": "Practice session deleted successfully"}


@router.get("/analytics/summary")
async def get_practice_analytics(
    days: int = 30,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """
    Get practice session analytics for the user
    
    Parameters:
    - days: Number of days to analyze (default: 30)
    """
    # Calculate date range
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Get all sessions in date range
    cursor = db.practice_sessions.find({
        "user_id": user_id,
        "created_at": {"$gte": start_date}
    })
    sessions = await cursor.to_list(length=1000)
    
    # Calculate analytics
    total_sessions = len(sessions)
    completed_sessions = len([s for s in sessions if s.get("completed", False)])
    total_questions_practiced = sum(s.get("questions_count", 0) for s in sessions)
    total_time_seconds = sum(s.get("duration_seconds", 0) for s in sessions)
    
    # Average session duration
    avg_duration = total_time_seconds / total_sessions if total_sessions > 0 else 0
    
    # Sessions by category (get questions and categorize)
    category_breakdown = {}
    for session in sessions:
        question_ids = session.get("question_ids", [])
        questions_cursor = db.interview_questions.find({
            "id": {"$in": question_ids},
            "user_id": user_id
        })
        questions = await questions_cursor.to_list(length=len(question_ids))
        
        for q in questions:
            category = q.get("category", "unknown")
            category_breakdown[category] = category_breakdown.get(category, 0) + 1
    
    # Recent activity (last 7 days)
    recent_start = datetime.utcnow() - timedelta(days=7)
    recent_sessions = [s for s in sessions if s.get("created_at") >= recent_start]
    
    # Completion rate
    completion_rate = (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0
    
    return {
        "period_days": days,
        "total_sessions": total_sessions,
        "completed_sessions": completed_sessions,
        "completion_rate": round(completion_rate, 1),
        "total_questions_practiced": total_questions_practiced,
        "total_time_seconds": total_time_seconds,
        "total_time_formatted": f"{total_time_seconds // 3600}h {(total_time_seconds % 3600) // 60}m",
        "average_session_duration_seconds": int(avg_duration),
        "average_session_duration_formatted": f"{int(avg_duration // 60)}m {int(avg_duration % 60)}s",
        "category_breakdown": category_breakdown,
        "recent_activity": {
            "last_7_days": len(recent_sessions),
            "questions_last_7_days": sum(s.get("questions_count", 0) for s in recent_sessions)
        },
        "streak": {
            "current": 0,  # TODO: Implement streak calculation
            "longest": 0
        }
    }
