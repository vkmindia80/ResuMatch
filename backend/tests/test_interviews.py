import pytest
from httpx import AsyncClient


@pytest.mark.interviews
class TestInterviews:
    """Test interview preparation endpoints"""
    
    @pytest.mark.asyncio
    async def test_get_categories(self, client: AsyncClient):
        """Test getting interview question categories"""
        response = await client.get("/api/interviews/categories")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert "id" in data[0]
        assert "name" in data[0]
    
    @pytest.mark.asyncio
    async def test_generate_questions_without_job(self, client: AsyncClient, auth_headers):
        """Test generating questions without job description (should fail)"""
        request_data = {
            "job_description_id": "00000000-0000-0000-0000-000000000000",
            "count": 10
        }
        response = await client.post("/api/interviews/generate-questions", json=request_data, headers=auth_headers)
        assert response.status_code == 404
        assert "job description not found" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_generate_questions_without_profile(self, client: AsyncClient, auth_headers, test_job):
        """Test generating questions without profile (should fail)"""
        request_data = {
            "job_description_id": test_job["id"],
            "count": 10
        }
        response = await client.post("/api/interviews/generate-questions", json=request_data, headers=auth_headers)
        assert response.status_code == 404
        assert "profile not found" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_generate_questions_success(self, client: AsyncClient, auth_headers, test_profile, test_job):
        """Test successfully generating interview questions"""
        request_data = {
            "job_description_id": test_job["id"],
            "count": 10
        }
        response = await client.post("/api/interviews/generate-questions", json=request_data, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert "questions" in data
        assert "count" in data
        assert data["count"] > 0
        assert len(data["questions"]) > 0
        
        # Check question structure
        question = data["questions"][0]
        assert "id" in question
        assert "question" in question
        assert "category" in question
        assert "difficulty" in question
        assert "ai_generated_answer" in question
    
    @pytest.mark.asyncio
    async def test_get_all_questions(self, client: AsyncClient, auth_headers, test_interview_question):
        """Test getting all interview questions for user with pagination"""
        response = await client.get("/api/interviews/questions", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert isinstance(data["items"], list)
        assert len(data["items"]) >= 1
        assert data["total"] >= 1
    
    @pytest.mark.asyncio
    async def test_get_questions_by_job(self, client: AsyncClient, auth_headers, test_interview_question, test_job):
        """Test filtering questions by job description"""
        response = await client.get(
            f"/api/interviews/questions?job_description_id={test_job['id']}", 
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # All returned questions should be for the specified job
        for question in data:
            assert question["job_description_id"] == test_job["id"]
    
    @pytest.mark.asyncio
    async def test_get_questions_by_category(self, client: AsyncClient, auth_headers, test_interview_question):
        """Test filtering questions by category"""
        response = await client.get(
            "/api/interviews/questions?category=behavioral",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # All returned questions should be of the specified category
        for question in data:
            if question.get("category"):
                assert question["category"] == "behavioral"
    
    @pytest.mark.asyncio
    async def test_interviews_unauthorized(self, client: AsyncClient):
        """Test accessing interview questions without authentication"""
        response = await client.get("/api/interviews/questions")
        assert response.status_code == 403
