import pytest
from httpx import AsyncClient


@pytest.mark.resumes
class TestResumes:
    """Test resume generation and management endpoints"""
    
    @pytest.mark.asyncio
    async def test_get_templates(self, client: AsyncClient):
        """Test getting available resume templates"""
        response = await client.get("/api/resumes/templates/list")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert "id" in data[0]
        assert "name" in data[0]
    
    @pytest.mark.asyncio
    async def test_generate_resume_without_profile(self, client: AsyncClient, auth_headers):
        """Test generating resume without a profile (should fail)"""
        resume_data = {
            "template_id": "template_1"
        }
        response = await client.post("/api/resumes/generate", json=resume_data, headers=auth_headers)
        assert response.status_code == 404
        assert "profile not found" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_generate_resume_basic(self, client: AsyncClient, auth_headers, test_profile):
        """Test generating a basic resume with profile"""
        resume_data = {
            "template_id": "template_1"
        }
        response = await client.post("/api/resumes/generate", json=resume_data, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["template_id"] == "template_1"
        assert data["status"] == "draft"
        assert "content" in data
        assert "ats_score" in data
    
    @pytest.mark.asyncio
    async def test_generate_resume_with_job(self, client: AsyncClient, auth_headers, test_profile, test_job):
        """Test generating resume optimized for a job description"""
        resume_data = {
            "job_description_id": test_job["id"],
            "template_id": "template_2"
        }
        response = await client.post("/api/resumes/generate", json=resume_data, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["job_description_id"] == test_job["id"]
        assert data["template_id"] == "template_2"
    
    @pytest.mark.asyncio
    async def test_get_all_resumes(self, client: AsyncClient, auth_headers, test_resume):
        """Test getting all resumes for user"""
        response = await client.get("/api/resumes/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
    
    @pytest.mark.asyncio
    async def test_get_resume_by_id(self, client: AsyncClient, auth_headers, test_resume):
        """Test getting specific resume by ID"""
        response = await client.get(f"/api/resumes/{test_resume['id']}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_resume["id"]
        assert "content" in data
        assert "ats_score" in data
    
    @pytest.mark.asyncio
    async def test_get_resume_not_found(self, client: AsyncClient, auth_headers):
        """Test getting non-existent resume"""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = await client.get(f"/api/resumes/{fake_id}", headers=auth_headers)
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_delete_resume(self, client: AsyncClient, auth_headers, test_resume):
        """Test deleting a resume"""
        response = await client.delete(f"/api/resumes/{test_resume['id']}", headers=auth_headers)
        assert response.status_code == 200
        
        # Verify resume is deleted
        get_response = await client.get(f"/api/resumes/{test_resume['id']}", headers=auth_headers)
        assert get_response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_resumes_unauthorized(self, client: AsyncClient):
        """Test accessing resumes without authentication"""
        response = await client.get("/api/resumes/")
        assert response.status_code == 403
