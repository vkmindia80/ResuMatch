"""
Load Testing Script for ResuMatch AI API
Tests critical endpoints with realistic user behavior
"""
from locust import HttpUser, task, between, events
import json
import random
from datetime import datetime

# Test credentials
TEST_USER_EMAIL = "loadtest@resumatch.com"
TEST_USER_PASSWORD = "LoadTest123!"


class ResuMatchUser(HttpUser):
    """
    Simulates a typical ResuMatch AI user workflow
    """
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    
    def on_start(self):
        """
        Called when a simulated user starts
        Performs login to get access token
        """
        # Try to register (might fail if user exists, that's ok)
        self.client.post("/api/auth/register", json={
            "full_name": f"Load Test User {random.randint(1000, 9999)}",
            "email": f"loadtest{random.randint(1000, 9999)}@resumatch.com",
            "password": TEST_USER_PASSWORD
        }, name="/api/auth/register")
        
        # Login to get token
        response = self.client.post("/api/auth/login", json={
            "email": f"loadtest{random.randint(1000, 9999)}@resumatch.com",
            "password": TEST_USER_PASSWORD
        }, name="/api/auth/login")
        
        # If login fails, try with demo credentials
        if response.status_code != 200:
            response = self.client.post("/api/auth/login", json={
                "email": "demo@resumatch.com",
                "password": "Demo@123"
            }, name="/api/auth/login")
        
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.token = None
            self.headers = {}
    
    @task(5)
    def view_dashboard(self):
        """
        Most common action - viewing the dashboard
        Weight: 5 (happens 5x more often than other tasks)
        """
        if not self.token:
            return
        
        # Get user info
        self.client.get("/api/auth/me", headers=self.headers, name="/api/auth/me")
        
        # Get profile
        self.client.get("/api/profiles/me", headers=self.headers, name="/api/profiles/me")
        
        # Get profile completeness
        self.client.get("/api/profiles/completeness", headers=self.headers, name="/api/profiles/completeness")
    
    @task(3)
    def view_jobs(self):
        """
        View job descriptions list
        Weight: 3
        """
        if not self.token:
            return
        
        self.client.get("/api/jobs/?skip=0&limit=10", headers=self.headers, name="/api/jobs/ (list)")
    
    @task(2)
    def create_job(self):
        """
        Create a new job description
        Weight: 2
        """
        if not self.token:
            return
        
        job_data = {
            "title": f"Software Engineer - Test {random.randint(100, 999)}",
            "company": f"Test Company {random.randint(1, 50)}",
            "location": random.choice(["Remote", "New York, NY", "San Francisco, CA", "Austin, TX"]),
            "job_type": random.choice(["Full-time", "Part-time", "Contract"]),
            "description": """
We are seeking a talented Software Engineer to join our team.

Requirements:
- 3+ years of experience in software development
- Strong knowledge of Python, JavaScript, or Java
- Experience with web frameworks (Django, React, Spring)
- Excellent problem-solving skills
- Bachelor's degree in Computer Science or related field

Responsibilities:
- Design and develop scalable web applications
- Collaborate with cross-functional teams
- Write clean, maintainable code
- Participate in code reviews
- Mentor junior developers

Benefits:
- Competitive salary
- Health insurance
- 401k matching
- Flexible work hours
- Professional development opportunities
            """.strip()
        }
        
        self.client.post("/api/jobs/", json=job_data, headers=self.headers, name="/api/jobs/ (create)")
    
    @task(3)
    def view_resumes(self):
        """
        View resumes list
        Weight: 3
        """
        if not self.token:
            return
        
        self.client.get("/api/resumes/?skip=0&limit=10", headers=self.headers, name="/api/resumes/ (list)")
    
    @task(1)
    def generate_resume(self):
        """
        Generate a resume (AI-powered, slower operation)
        Weight: 1 (less frequent due to cost)
        """
        if not self.token:
            return
        
        # First, get a job (or use a random job_id if you have one)
        jobs_response = self.client.get("/api/jobs/?skip=0&limit=1", headers=self.headers, name="/api/jobs/ (for resume)")
        
        if jobs_response.status_code == 200:
            jobs = jobs_response.json().get("jobs", [])
            if jobs:
                job_id = jobs[0].get("_id")
                
                resume_data = {
                    "job_description_id": job_id,
                    "template_id": random.choice(["modern", "classic", "professional"]),
                    "customizations": {
                        "colors": {"primary": "#2563eb", "secondary": "#64748b"},
                        "fonts": {"heading": "Inter", "body": "Inter"},
                        "layout": "single-column"
                    }
                }
                
                self.client.post("/api/resumes/generate", json=resume_data, headers=self.headers, name="/api/resumes/generate")
    
    @task(2)
    def view_interview_questions(self):
        """
        View interview questions
        Weight: 2
        """
        if not self.token:
            return
        
        self.client.get("/api/interviews/questions?skip=0&limit=10", headers=self.headers, name="/api/interviews/questions")
    
    @task(1)
    def generate_interview_questions(self):
        """
        Generate interview questions (AI-powered)
        Weight: 1
        """
        if not self.token:
            return
        
        # Get a job first
        jobs_response = self.client.get("/api/jobs/?skip=0&limit=1", headers=self.headers, name="/api/jobs/ (for interview)")
        
        if jobs_response.status_code == 200:
            jobs = jobs_response.json().get("jobs", [])
            if jobs:
                job_id = jobs[0].get("_id")
                
                interview_data = {
                    "job_description_id": job_id,
                    "question_count": 10,
                    "categories": ["behavioral", "technical", "company_culture"]
                }
                
                self.client.post("/api/interviews/generate-questions", json=interview_data, headers=self.headers, name="/api/interviews/generate-questions")
    
    @task(1)
    def health_check(self):
        """
        Health check endpoint
        Weight: 1
        """
        self.client.get("/api/health", name="/api/health")


class QuickUser(HttpUser):
    """
    Simulates users who only check health and basic endpoints
    For testing high-traffic scenarios
    """
    wait_time = between(0.5, 1)
    
    @task(10)
    def root(self):
        self.client.get("/", name="/ (root)")
    
    @task(5)
    def health(self):
        self.client.get("/api/health", name="/api/health (quick)")


# Event listeners for reporting
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    print("\n" + "="*60)
    print("🚀 Load Test Starting - ResuMatch AI")
    print("="*60)
    print(f"Target: {environment.host}")
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60 + "\n")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    print("\n" + "="*60)
    print("✅ Load Test Complete - ResuMatch AI")
    print("="*60)
    print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60 + "\n")
    
    # Print summary
    stats = environment.stats
    print("\n📊 PERFORMANCE SUMMARY")
    print("-" * 60)
    print(f"Total Requests: {stats.total.num_requests}")
    print(f"Total Failures: {stats.total.num_failures}")
    print(f"Average Response Time: {stats.total.avg_response_time:.2f}ms")
    print(f"Min Response Time: {stats.total.min_response_time:.2f}ms")
    print(f"Max Response Time: {stats.total.max_response_time:.2f}ms")
    print(f"Requests per Second: {stats.total.total_rps:.2f}")
    print(f"Failure Rate: {(stats.total.num_failures / stats.total.num_requests * 100) if stats.total.num_requests > 0 else 0:.2f}%")
    print("-" * 60 + "\n")
