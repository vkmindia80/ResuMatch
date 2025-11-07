"""
Quick Load Test - Simple verification
Tests basic endpoints without AI features
"""
from locust import HttpUser, task, between
import random


class QuickTestUser(HttpUser):
    """Simple user for quick testing"""
    wait_time = between(1, 2)
    
    def on_start(self):
        """Login with demo credentials"""
        response = self.client.post("/api/auth/login", json={
            "email": "demo@resumatch.com",
            "password": "Demo@123"
        })
        
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.token = None
            self.headers = {}
    
    @task(10)
    def health_check(self):
        """Health check - most frequent"""
        self.client.get("/api/health")
    
    @task(5)
    def root(self):
        """Root endpoint"""
        self.client.get("/")
    
    @task(3)
    def get_profile(self):
        """Get user profile"""
        if self.token:
            self.client.get("/api/profiles/me", headers=self.headers)
    
    @task(3)
    def get_jobs(self):
        """Get jobs list"""
        if self.token:
            self.client.get("/api/jobs/?skip=0&limit=10", headers=self.headers)
    
    @task(2)
    def get_resumes(self):
        """Get resumes list"""
        if self.token:
            self.client.get("/api/resumes/?skip=0&limit=10", headers=self.headers)
