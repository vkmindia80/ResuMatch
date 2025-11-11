#!/usr/bin/env python3
"""
Setup test data for Live Interview Assistant testing
"""

import requests
import json

BASE_URL = "http://localhost:8001"

def login():
    """Login and get token"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={
            "email": "testuser@test.com",
            "password": "testpass123"
        }
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    return None

def create_profile(token):
    """Create a test profile"""
    headers = {"Authorization": f"Bearer {token}"}
    
    profile_data = {
        "personal_info": {
            "full_name": "Test User",
            "email": "testuser@test.com",
            "phone": "+1-555-0123",
            "location": "San Francisco, CA",
            "title": "Senior Software Engineer",
            "linkedin": "https://linkedin.com/in/testuser",
            "portfolio": "https://testuser.dev"
        },
        "professional_summary": "Experienced software engineer with 5+ years of expertise in full-stack development, specializing in Python, React, and cloud technologies. Proven track record of delivering scalable applications and leading technical teams.",
        "experience": [
            {
                "title": "Senior Software Engineer",
                "company": "Tech Corp",
                "location": "San Francisco, CA",
                "start_date": "2020-01-01",
                "end_date": None,
                "current": True,
                "description": "Led development of microservices architecture",
                "responsibilities": [
                    "Architected and implemented scalable microservices using Python and FastAPI",
                    "Managed team of 4 junior developers",
                    "Reduced API response time by 40%"
                ],
                "achievements": [
                    "Implemented CI/CD pipeline reducing deployment time by 60%",
                    "Led migration to cloud infrastructure (AWS)"
                ],
                "technologies": ["Python", "FastAPI", "React", "AWS", "Docker"]
            },
            {
                "title": "Software Engineer",
                "company": "StartUp Inc",
                "location": "Remote",
                "start_date": "2018-06-01",
                "end_date": "2019-12-31",
                "current": False,
                "description": "Full-stack development",
                "responsibilities": [
                    "Developed RESTful APIs using Django",
                    "Built responsive frontends with React"
                ],
                "achievements": [
                    "Launched product serving 10K+ users"
                ],
                "technologies": ["Python", "Django", "React", "PostgreSQL"]
            }
        ],
        "skills": {
            "technical": [
                {"name": "Python", "level": "expert"},
                {"name": "JavaScript", "level": "expert"},
                {"name": "React", "level": "advanced"},
                {"name": "FastAPI", "level": "expert"},
                {"name": "AWS", "level": "intermediate"}
            ],
            "soft": ["Leadership", "Communication", "Problem Solving"],
            "tools": ["Git", "Docker", "Kubernetes", "Jenkins"],
            "languages": ["English (Native)", "Spanish (Conversational)"]
        },
        "education": [
            {
                "institution": "University of California",
                "degree": "Bachelor of Science",
                "field": "Computer Science",
                "start_date": "2014-09-01",
                "end_date": "2018-05-31",
                "gpa": 3.8,
                "achievements": ["Dean's List", "CS Department Award"]
            }
        ],
        "certifications": [
            {
                "name": "AWS Solutions Architect",
                "issuer": "Amazon Web Services",
                "date": "2021-06-15"
            }
        ]
    }
    
    response = requests.post(
        f"{BASE_URL}/api/profiles/me",
        json=profile_data,
        headers=headers
    )
    
    if response.status_code in [200, 201]:
        print("✅ Profile created successfully")
        return True
    else:
        print(f"❌ Failed to create profile: {response.status_code}")
        print(response.text)
        return False

def create_job(token):
    """Create a test job description"""
    headers = {"Authorization": f"Bearer {token}"}
    
    job_data = {
        "title": "Senior Backend Engineer",
        "company": "TechCorp",
        "location": "San Francisco, CA",
        "description": "We are seeking an experienced backend engineer to join our team.",
        "requirements": "5+ years Python experience, FastAPI, microservices, AWS",
        "responsibilities": "Design and implement scalable backend services",
        "benefits": "Competitive salary, equity, health insurance",
        "salary_range": "$150,000 - $200,000",
        "employment_type": "Full-time"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/jobs/",
        json=job_data,
        headers=headers
    )
    
    if response.status_code in [200, 201]:
        print("✅ Job description created successfully")
        return response.json().get("id")
    else:
        print(f"❌ Failed to create job: {response.status_code}")
        return None

def create_resume(token, job_id):
    """Generate a test resume"""
    headers = {"Authorization": f"Bearer {token}"}
    
    resume_data = {
        "job_description_id": job_id,
        "template_id": "template_1"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/resumes/generate",
        json=resume_data,
        headers=headers
    )
    
    if response.status_code in [200, 201]:
        print("✅ Resume generated successfully")
        return response.json().get("id")
    else:
        print(f"❌ Failed to generate resume: {response.status_code}")
        print(response.text)
        return None

def main():
    print("🔧 Setting up test data for Live Interview Assistant...")
    
    token = login()
    if not token:
        print("❌ Failed to login")
        return
    
    print("✅ Logged in successfully")
    
    # Create profile
    if not create_profile(token):
        return
    
    # Create job
    job_id = create_job(token)
    if not job_id:
        return
    
    # Generate resume
    resume_id = create_resume(token, job_id)
    if not resume_id:
        return
    
    print("\n🎉 Test data setup complete!")
    print(f"   Job ID: {job_id}")
    print(f"   Resume ID: {resume_id}")

if __name__ == "__main__":
    main()
