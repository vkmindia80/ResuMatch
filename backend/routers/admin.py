"""
Admin API Routes
Manage application settings including storage configuration and AI integrations
"""
from fastapi import APIRouter, HTTPException, status, Depends
from models.settings import (
    StorageSettings, StorageSettingsUpdate, AppSettings,
    AISettings, AISettingsUpdate, UserAISettings, UserAISettingsUpdate
)
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


@router.post("/generate-sample-data")
async def generate_sample_data(
    target_user_email: Optional[str] = None,
    db = Depends(get_database)
):
    """
    Generate comprehensive sample data across all modules
    Can be called without authentication to populate demo user
    Or with target_user_email to populate specific user
    """
    try:
        # Determine target user
        if target_user_email:
            user = await db.users.find_one({"email": target_user_email})
        else:
            # Default to demo user
            user = await db.users.find_one({"email": "demo@resumatch.com"})
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_id = user["id"]
        
        # Track what was created
        created = {
            "profiles": 0,
            "job_descriptions": 0,
            "resumes": 0,
            "interview_questions": 0,
            "cover_letters": 0,
            "practice_sessions": 0,
            "live_interview_sessions": 0
        }
        
        # 1. Create/Update Profile
        existing_profile = await db.profiles.find_one({"user_id": user_id})
        
        if not existing_profile:
            profile_data = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "personal_info": {
                    "full_name": user.get("full_name", "Demo User"),
                    "email": user.get("email"),
                    "phone": "+1-555-0100",
                    "location": "New York, NY",
                    "title": "Senior Product Manager",
                    "linkedin": "https://linkedin.com/in/demoprofile",
                    "portfolio": "https://demoportfolio.com"
                },
                "summary": "Experienced professional with 8+ years across technology, healthcare, and marketing sectors. Proven track record of leading cross-functional teams and delivering impactful results.",
                "skills": {
                    "technical": [
                        {"name": "Python", "level": "expert"},
                        {"name": "JavaScript", "level": "advanced"},
                        {"name": "SQL", "level": "expert"},
                        {"name": "Data Analysis", "level": "expert"},
                        {"name": "Project Management", "level": "expert"}
                    ],
                    "soft": ["Leadership", "Communication", "Strategic Planning", "Team Building", "Problem Solving"],
                    "tools": ["Jira", "Salesforce", "Tableau", "Git", "Figma"],
                    "languages": [
                        {"name": "English", "fluency": "Native"},
                        {"name": "Spanish", "fluency": "Professional"}
                    ]
                },
                "experience": [
                    {
                        "title": "Senior Product Manager",
                        "company": "TechVision Inc",
                        "location": "New York, NY",
                        "start_date": "2021-03-01",
                        "end_date": None,
                        "current": True,
                        "description": "Leading product strategy for SaaS platform serving 50K+ users",
                        "responsibilities": [
                            "Define product roadmap and vision for enterprise SaaS platform",
                            "Manage cross-functional team of 12 engineers, designers, and analysts",
                            "Drive go-to-market strategy resulting in 150% revenue growth"
                        ],
                        "achievements": [
                            "Launched 3 major features increasing user engagement by 45%",
                            "Reduced customer churn from 8% to 3% through data-driven improvements"
                        ],
                        "technologies": ["Python", "SQL", "Tableau", "Jira"]
                    },
                    {
                        "title": "Marketing Manager",
                        "company": "HealthPlus Medical",
                        "location": "Boston, MA",
                        "start_date": "2018-06-01",
                        "end_date": "2021-02-28",
                        "current": False,
                        "description": "Led digital marketing initiatives for healthcare services",
                        "responsibilities": [
                            "Managed $500K annual marketing budget",
                            "Developed and executed multi-channel campaigns",
                            "Analyzed campaign performance and optimized ROI"
                        ],
                        "achievements": [
                            "Increased patient acquisition by 60% year-over-year",
                            "Achieved 300% ROI on digital advertising spend"
                        ],
                        "technologies": ["Salesforce", "Google Analytics", "HubSpot"]
                    },
                    {
                        "title": "Financial Analyst",
                        "company": "Global Finance Corp",
                        "location": "Chicago, IL",
                        "start_date": "2016-07-01",
                        "end_date": "2018-05-31",
                        "current": False,
                        "description": "Performed financial modeling and analysis",
                        "responsibilities": [
                            "Built financial models for investment decisions",
                            "Conducted market research and competitive analysis",
                            "Prepared reports for senior management"
                        ],
                        "achievements": [
                            "Identified cost-saving opportunities worth $2M annually",
                            "Improved forecasting accuracy by 25%"
                        ],
                        "technologies": ["Excel", "SQL", "Tableau", "Python"]
                    }
                ],
                "education": [
                    {
                        "institution": "Boston University",
                        "degree": "Master of Business Administration",
                        "field": "Business Administration",
                        "start_date": "2014-09-01",
                        "end_date": "2016-05-31",
                        "gpa": 3.9,
                        "achievements": ["Dean's List", "Outstanding MBA Student Award"]
                    },
                    {
                        "institution": "University of Illinois",
                        "degree": "Bachelor of Science",
                        "field": "Economics",
                        "start_date": "2010-09-01",
                        "end_date": "2014-05-31",
                        "gpa": 3.7,
                        "achievements": ["Magna Cum Laude", "Economics Department Honors"]
                    }
                ],
                "certifications": [
                    {
                        "name": "Project Management Professional (PMP)",
                        "issuer": "Project Management Institute",
                        "issue_date": "2020-08-15",
                        "expiry_date": "2023-08-15"
                    },
                    {
                        "name": "Certified Scrum Product Owner",
                        "issuer": "Scrum Alliance",
                        "issue_date": "2021-03-20"
                    }
                ],
                "projects": [],
                "completeness_score": 95,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            await db.profiles.insert_one(profile_data)
            created["profiles"] = 1
        
        # 2. Create Job Descriptions (diverse roles)
        job_descriptions = [
            {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "title": "Senior Product Manager",
                "company": "InnovateTech Solutions",
                "location": "San Francisco, CA (Remote)",
                "description": "We're seeking an experienced Product Manager to lead our enterprise SaaS product line. You'll work with engineering, design, and sales teams to drive product strategy and execution.",
                "requirements": "5+ years product management experience, strong analytical skills, experience with SaaS products, excellent communication",
                "responsibilities": "Define product roadmap, prioritize features, conduct market research, work with cross-functional teams",
                "benefits": "Competitive salary, equity, health insurance, 401k matching, unlimited PTO",
                "salary_range": "$140,000 - $180,000",
                "employment_type": "Full-time",
                "created_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "title": "Marketing Director",
                "company": "HealthCare Innovations",
                "location": "Boston, MA",
                "description": "Lead our marketing team to drive patient acquisition and brand awareness for our healthcare services platform.",
                "requirements": "7+ years marketing experience, healthcare industry knowledge, budget management, team leadership",
                "responsibilities": "Develop marketing strategy, manage team of 8, oversee campaigns, analyze ROI, collaborate with sales",
                "benefits": "Competitive salary, bonus, comprehensive health benefits, flexible work",
                "salary_range": "$120,000 - $160,000",
                "employment_type": "Full-time",
                "created_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "title": "Senior Data Analyst",
                "company": "FinTech Global",
                "location": "New York, NY",
                "description": "Join our analytics team to provide insights that drive business decisions in the financial services sector.",
                "requirements": "4+ years data analysis, SQL expert, Python/R, financial industry experience, data visualization",
                "responsibilities": "Analyze large datasets, create dashboards, provide actionable insights, collaborate with stakeholders",
                "benefits": "Competitive compensation, bonus, stock options, health benefits",
                "salary_range": "$100,000 - $140,000",
                "employment_type": "Full-time",
                "created_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "title": "Software Engineering Manager",
                "company": "CloudScale Technologies",
                "location": "Seattle, WA",
                "description": "Lead a team of talented engineers building next-generation cloud infrastructure solutions.",
                "requirements": "8+ years software development, 3+ years management, cloud technologies, Python/Java, leadership",
                "responsibilities": "Manage engineering team, technical architecture, code reviews, hiring, mentoring",
                "benefits": "Excellent compensation, equity, health benefits, learning budget",
                "salary_range": "$170,000 - $220,000",
                "employment_type": "Full-time",
                "created_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "title": "UX Design Lead",
                "company": "Creative Studio Co",
                "location": "Austin, TX (Hybrid)",
                "description": "Shape the user experience for our portfolio of mobile and web applications.",
                "requirements": "6+ years UX design, portfolio required, Figma/Sketch, user research, design systems",
                "responsibilities": "Lead design projects, conduct user research, create prototypes, mentor junior designers",
                "benefits": "Competitive salary, creative environment, flexible schedule, health benefits",
                "salary_range": "$110,000 - $150,000",
                "employment_type": "Full-time",
                "created_at": datetime.utcnow()
            }
        ]
        
        for job in job_descriptions:
            await db.job_descriptions.insert_one(job)
            created["job_descriptions"] += 1
        
        # 3. Create Interview Questions (for first 2 jobs)
        interview_questions_sets = [
            {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "job_description_id": job_descriptions[0]["id"],
                "questions": [
                    {
                        "question": "Tell me about a time when you had to make a difficult product decision with limited data.",
                        "category": "behavioral",
                        "suggested_answer": "In my role at TechVision, we were deciding whether to build a new feature requested by several enterprise clients...",
                        "star_format": {
                            "situation": "Several enterprise clients requested a complex reporting feature",
                            "task": "Evaluate if we should prioritize this over other roadmap items",
                            "action": "Conducted user interviews, analyzed usage data, estimated development cost",
                            "result": "Decided to build simplified version, launched in 6 weeks, 80% adoption"
                        }
                    },
                    {
                        "question": "How do you prioritize features on your product roadmap?",
                        "category": "technical",
                        "suggested_answer": "I use a combination of frameworks including RICE scoring (Reach, Impact, Confidence, Effort)..."
                    },
                    {
                        "question": "Describe your experience working with cross-functional teams.",
                        "category": "behavioral",
                        "suggested_answer": "At TechVision, I work daily with engineering, design, sales, and support teams..."
                    }
                ],
                "created_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "job_description_id": job_descriptions[1]["id"],
                "questions": [
                    {
                        "question": "Tell me about a successful marketing campaign you've led.",
                        "category": "behavioral",
                        "suggested_answer": "At HealthPlus Medical, I led a digital campaign targeting new patient acquisition...",
                        "star_format": {
                            "situation": "Needed to increase patient acquisition in competitive market",
                            "task": "Develop and execute integrated marketing campaign",
                            "action": "Created multi-channel campaign with SEO, PPC, and content marketing",
                            "result": "60% increase in patient acquisition, 300% ROI"
                        }
                    },
                    {
                        "question": "How do you measure marketing ROI?",
                        "category": "technical",
                        "suggested_answer": "I track multiple metrics including CAC, LTV, conversion rates, and channel-specific ROI..."
                    }
                ],
                "created_at": datetime.utcnow()
            }
        ]
        
        for questions_set in interview_questions_sets:
            await db.interview_questions.insert_one(questions_set)
            created["interview_questions"] += 1
        
        # 4. Create Resumes (for first 3 jobs)
        resumes = [
            {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "job_description_id": job_descriptions[0]["id"],
                "template_id": "template_1",
                "content": {
                    "personal_info": {
                        "name": user.get("full_name", "Demo User"),
                        "email": user.get("email"),
                        "phone": "+1-555-0100",
                        "location": "New York, NY",
                        "linkedin": "linkedin.com/in/demoprofile"
                    },
                    "summary": "Results-driven Senior Product Manager with 8+ years of experience driving product strategy and execution for enterprise SaaS platforms. Proven track record of launching features that increase engagement by 45% and reduce churn by 60%.",
                    "experience": [
                        {
                            "title": "Senior Product Manager",
                            "company": "TechVision Inc",
                            "duration": "2021 - Present",
                            "highlights": [
                                "Define product roadmap for SaaS platform serving 50K+ users",
                                "Led cross-functional team delivering 150% revenue growth",
                                "Launched 3 major features increasing engagement by 45%"
                            ]
                        }
                    ],
                    "skills": ["Product Strategy", "Agile/Scrum", "Data Analysis", "SQL", "Python", "Leadership"],
                    "education": [
                        {
                            "degree": "MBA",
                            "institution": "Boston University",
                            "year": "2016"
                        }
                    ]
                },
                "ats_score": 92,
                "created_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "job_description_id": job_descriptions[1]["id"],
                "template_id": "template_2",
                "content": {
                    "personal_info": {
                        "name": user.get("full_name", "Demo User"),
                        "email": user.get("email"),
                        "phone": "+1-555-0100",
                        "location": "New York, NY"
                    },
                    "summary": "Strategic Marketing Director with 8+ years driving patient acquisition and brand awareness in healthcare. Achieved 60% YoY growth and 300% ROI on digital campaigns.",
                    "experience": [
                        {
                            "title": "Marketing Manager",
                            "company": "HealthPlus Medical",
                            "duration": "2018 - 2021",
                            "highlights": [
                                "Managed $500K marketing budget",
                                "Increased patient acquisition by 60% YoY",
                                "Achieved 300% ROI on digital advertising"
                            ]
                        }
                    ],
                    "skills": ["Digital Marketing", "Campaign Management", "Salesforce", "Data Analysis", "Team Leadership"]
                },
                "ats_score": 88,
                "created_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "job_description_id": job_descriptions[2]["id"],
                "template_id": "template_1",
                "content": {
                    "personal_info": {
                        "name": user.get("full_name", "Demo User"),
                        "email": user.get("email"),
                        "phone": "+1-555-0100",
                        "location": "New York, NY"
                    },
                    "summary": "Senior Data Analyst with 7+ years in financial services. Expert in SQL, Python, and data visualization. Track record of identifying $2M cost savings and improving forecasting accuracy by 25%.",
                    "experience": [
                        {
                            "title": "Financial Analyst",
                            "company": "Global Finance Corp",
                            "duration": "2016 - 2018",
                            "highlights": [
                                "Built financial models for investment decisions",
                                "Identified $2M in annual cost savings",
                                "Improved forecasting accuracy by 25%"
                            ]
                        }
                    ],
                    "skills": ["SQL", "Python", "Tableau", "Financial Modeling", "Data Analysis"]
                },
                "ats_score": 90,
                "created_at": datetime.utcnow()
            }
        ]
        
        for resume in resumes:
            await db.resumes.insert_one(resume)
            created["resumes"] += 1
        
        # 5. Create Cover Letters
        cover_letters = [
            {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "job_description_id": job_descriptions[0]["id"],
                "content": f"""Dear Hiring Manager,

I am writing to express my strong interest in the Senior Product Manager position at InnovateTech Solutions. With over 8 years of experience in product management and a proven track record of driving product strategy for enterprise SaaS platforms, I am confident I would be a valuable addition to your team.

In my current role at TechVision Inc, I have successfully led the product strategy for a platform serving 50,000+ users, resulting in 150% revenue growth. I launched three major features that increased user engagement by 45% and reduced customer churn from 8% to 3% through data-driven improvements.

What particularly excites me about this opportunity is your focus on innovation and customer-centric product development. My experience in managing cross-functional teams, combined with my strong analytical skills and passion for solving complex problems, aligns perfectly with your requirements.

I would welcome the opportunity to discuss how my experience and skills can contribute to InnovateTech Solutions' continued success.

Best regards,
{user.get("full_name", "Demo User")}""",
                "created_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "job_description_id": job_descriptions[1]["id"],
                "content": f"""Dear Hiring Manager,

I am excited to apply for the Marketing Director position at HealthCare Innovations. With 8 years of marketing experience, including 3 years specifically in healthcare, I have a deep understanding of the unique challenges and opportunities in this sector.

At HealthPlus Medical, I led digital marketing initiatives that increased patient acquisition by 60% year-over-year while achieving a 300% ROI on our digital advertising spend. I managed a $500K annual budget and developed multi-channel campaigns that resonated with our target audience.

I am particularly drawn to HealthCare Innovations' mission of making healthcare more accessible. My combination of marketing expertise, healthcare industry knowledge, and proven leadership skills makes me an ideal fit for this role.

I look forward to the opportunity to discuss how I can contribute to your team's success.

Sincerely,
{user.get("full_name", "Demo User")}""",
                "created_at": datetime.utcnow()
            }
        ]
        
        for letter in cover_letters:
            await db.cover_letters.insert_one(letter)
            created["cover_letters"] += 1
        
        # 6. Create Practice Sessions
        practice_sessions = [
            {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "job_description_id": job_descriptions[0]["id"],
                "title": "Product Manager Interview Practice",
                "session_type": "mock_interview",
                "status": "completed",
                "duration_minutes": 45,
                "questions_count": 5,
                "score": 85,
                "feedback": "Strong performance overall. Good use of STAR method. Could improve on quantifying impact more specifically.",
                "created_at": datetime.utcnow(),
                "completed_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "job_description_id": job_descriptions[1]["id"],
                "title": "Marketing Director Behavioral Questions",
                "session_type": "behavioral",
                "status": "completed",
                "duration_minutes": 30,
                "questions_count": 3,
                "score": 78,
                "feedback": "Good examples provided. Consider adding more specific metrics to strengthen answers.",
                "created_at": datetime.utcnow(),
                "completed_at": datetime.utcnow()
            }
        ]
        
        for session in practice_sessions:
            await db.practice_sessions.insert_one(session)
            created["practice_sessions"] += 1
        
        # 7. Create Live Interview Session
        live_session = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": "InnovateTech Product Manager Interview",
            "job_description_id": job_descriptions[0]["id"],
            "status": "completed",
            "ai_model": "gpt-4o",
            "language": "en-US",
            "duration_seconds": 2700,
            "questions_count": 8,
            "started_at": datetime.utcnow(),
            "ended_at": datetime.utcnow(),
            "created_at": datetime.utcnow()
        }
        
        await db.live_interview_sessions.insert_one(live_session)
        created["live_interview_sessions"] = 1
        
        # Add some transcript entries for the live session
        transcripts = [
            {
                "id": str(uuid.uuid4()),
                "session_id": live_session["id"],
                "question": "Tell me about yourself and your experience in product management.",
                "answer": "I'm a Senior Product Manager with 8 years of experience. Currently at TechVision Inc, I lead product strategy for our SaaS platform serving 50K+ users. I've successfully launched multiple features that increased engagement by 45% and reduced churn significantly.",
                "timestamp": datetime.utcnow(),
                "created_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "session_id": live_session["id"],
                "question": "How do you prioritize features on your product roadmap?",
                "answer": "I use a combination of frameworks, primarily RICE scoring - Reach, Impact, Confidence, and Effort. I also consider strategic alignment, customer feedback, and technical dependencies. Regular stakeholder communication ensures we're building the right things.",
                "timestamp": datetime.utcnow(),
                "created_at": datetime.utcnow()
            }
        ]
        
        for transcript in transcripts:
            await db.interview_transcripts.insert_one(transcript)
        
        # Return summary
        return {
            "success": True,
            "message": "Sample data generated successfully",
            "user_email": user.get("email"),
            "created": created,
            "total_items": sum(created.values())
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate sample data: {str(e)}"
        )


# ============================================
# AI CONFIGURATION ENDPOINTS
# ============================================

@router.get("/ai-settings")
async def get_ai_settings(
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """
    Get admin AI configuration settings (defaults for all users)
    """
    settings_doc = await db.settings.find_one({"type": "ai"})
    
    if settings_doc:
        settings_doc.pop("_id", None)
        return settings_doc
    
    # Return default settings
    default_settings = AISettings()
    return {
        "type": "ai",
        **default_settings.model_dump()
    }


@router.put("/ai-settings")
async def update_ai_settings(
    settings: AISettingsUpdate,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """
    Update admin AI configuration settings
    Note: In production, add admin check here
    """
    try:
        # Get existing settings or create new
        existing = await db.settings.find_one({"type": "ai"})
        
        if existing:
            # Update existing
            update_data = settings.model_dump(exclude_unset=True)
            update_data["updated_at"] = datetime.utcnow()
            update_data["updated_by"] = user_id
            
            # Merge with existing data
            for key, value in update_data.items():
                if value is not None:
                    existing[key] = value
            
            await db.settings.update_one(
                {"type": "ai"},
                {"$set": existing}
            )
            
            existing.pop("_id", None)
            return {
                "success": True,
                "message": "AI settings updated successfully",
                "settings": existing
            }
        else:
            # Create new
            settings_doc = {
                "type": "ai",
                **settings.model_dump(exclude_unset=True),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "updated_by": user_id
            }
            
            await db.settings.insert_one(settings_doc)
            settings_doc.pop("_id", None)
            
            return {
                "success": True,
                "message": "AI settings created successfully",
                "settings": settings_doc
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update AI settings: {str(e)}"
        )


@router.get("/ai-settings/user")
async def get_user_ai_settings(
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """
    Get user-specific AI settings (overrides admin defaults)
    """
    settings_doc = await db.user_ai_settings.find_one({"user_id": user_id})
    
    if settings_doc:
        settings_doc.pop("_id", None)
        return settings_doc
    
    # Return empty user settings (means using admin defaults)
    return {
        "user_id": user_id,
        "use_custom_keys": False,
        "openai": None,
        "anthropic": None,
        "google": None,
        "custom": None,
        "resume_generation": None,
        "interview_prep": None,
        "cover_letter": None,
        "live_interview": None,
        "ats_optimization": None
    }


@router.put("/ai-settings/user")
async def update_user_ai_settings(
    settings: UserAISettingsUpdate,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """
    Update user-specific AI settings
    """
    try:
        # Get existing settings or create new
        existing = await db.user_ai_settings.find_one({"user_id": user_id})
        
        if existing:
            # Update existing
            update_data = settings.model_dump(exclude_unset=True)
            update_data["updated_at"] = datetime.utcnow()
            
            # Merge with existing data
            for key, value in update_data.items():
                if value is not None:
                    existing[key] = value
            
            await db.user_ai_settings.update_one(
                {"user_id": user_id},
                {"$set": existing}
            )
            
            existing.pop("_id", None)
            return {
                "success": True,
                "message": "Your AI settings updated successfully",
                "settings": existing
            }
        else:
            # Create new
            settings_doc = {
                "user_id": user_id,
                **settings.model_dump(exclude_unset=True),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            await db.user_ai_settings.insert_one(settings_doc)
            settings_doc.pop("_id", None)
            
            return {
                "success": True,
                "message": "Your AI settings created successfully",
                "settings": settings_doc
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user AI settings: {str(e)}"
        )


@router.delete("/ai-settings/user")
async def reset_user_ai_settings(
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """
    Reset user AI settings to admin defaults
    """
    try:
        result = await db.user_ai_settings.delete_one({"user_id": user_id})
        
        if result.deleted_count > 0:
            return {
                "success": True,
                "message": "AI settings reset to defaults"
            }
        else:
            return {
                "success": True,
                "message": "No custom settings found, using defaults"
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset AI settings: {str(e)}"
        )


@router.get("/ai-settings/effective")
async def get_effective_ai_settings(
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """
    Get effective AI settings (user overrides merged with admin defaults)
    """
    try:
        # Get admin defaults
        admin_settings = await db.settings.find_one({"type": "ai"})
        if not admin_settings:
            admin_settings = {"type": "ai", **AISettings().model_dump()}
        
        # Get user settings
        user_settings = await db.user_ai_settings.find_one({"user_id": user_id})
        
        # Merge settings (user overrides admin)
        effective = dict(admin_settings)
        effective.pop("_id", None)
        
        if user_settings:
            user_settings.pop("_id", None)
            # Override with user settings where they exist
            for key, value in user_settings.items():
                if value is not None and key != "user_id":
                    effective[key] = value
        
        effective["is_using_custom_settings"] = bool(user_settings and user_settings.get("use_custom_keys"))
        
        return {
            "success": True,
            "settings": effective,
            "has_user_overrides": bool(user_settings)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get effective AI settings: {str(e)}"
        )
