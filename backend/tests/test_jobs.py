import pytest
from httpx import AsyncClient


@pytest.mark.jobs
class TestJobDescriptions:
    """Test job description endpoints"""
    
    @pytest.mark.asyncio
    async def test_create_job(self, client: AsyncClient, auth_headers):
        """Test creating a job description"""
        job_data = {
            "title": "Software Engineer",
            "company": "Test Corp",
            "location": "Remote",
            "job_type": "Full-time",
            "description": "We are looking for a software engineer with Python experience..."
        }
        response = await client.post("/api/jobs/", json=job_data, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == job_data["title"]
        assert data["company"] == job_data["company"]
        assert "id" in data
    
    @pytest.mark.asyncio
    async def test_get_all_jobs(self, client: AsyncClient, auth_headers, test_job):
        """Test getting all job descriptions"""
        response = await client.get("/api/jobs/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
    
    @pytest.mark.asyncio
    async def test_get_job_by_id(self, client: AsyncClient, auth_headers, test_job):
        """Test getting specific job description"""
        response = await client.get(f"/api/jobs/{test_job['id']}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_job["id"]
        assert data["title"] == test_job["title"]
    
    @pytest.mark.asyncio
    async def test_get_job_not_found(self, client: AsyncClient, auth_headers):
        """Test getting non-existent job"""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = await client.get(f"/api/jobs/{fake_id}", headers=auth_headers)
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_update_job(self, client: AsyncClient, auth_headers, test_job):
        """Test updating job description"""
        update_data = {
            "title": "Senior Software Engineer",
            "location": "San Francisco, CA"
        }
        response = await client.put(f"/api/jobs/{test_job['id']}", json=update_data, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == update_data["title"]
    
    @pytest.mark.asyncio
    async def test_delete_job(self, client: AsyncClient, auth_headers, test_job):
        """Test deleting job description"""
        response = await client.delete(f"/api/jobs/{test_job['id']}", headers=auth_headers)
        assert response.status_code == 200
        
        # Verify job is deleted
        get_response = await client.get(f"/api/jobs/{test_job['id']}", headers=auth_headers)
        assert get_response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_jobs_unauthorized(self, client: AsyncClient):
        """Test accessing jobs without authentication"""
        response = await client.get("/api/jobs/")
        assert response.status_code == 403
