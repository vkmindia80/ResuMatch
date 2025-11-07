import pytest
from httpx import AsyncClient


@pytest.mark.profile
class TestProfiles:
    """Test profile endpoints"""
    
    @pytest.mark.asyncio
    async def test_create_profile(self, client: AsyncClient, auth_headers):
        """Test creating a new profile"""
        profile_data = {
            "full_name": "Test User",
            "email": "test@example.com",
            "phone": "+1234567890",
            "location": "San Francisco, CA",
            "title": "Software Engineer"
        }
        response = await client.post("/api/profiles/me", json=profile_data, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["personal_info"]["full_name"] == profile_data["full_name"]
        assert data["personal_info"]["email"] == profile_data["email"]
        assert "id" in data
    
    @pytest.mark.asyncio
    async def test_get_profile(self, client: AsyncClient, auth_headers, test_profile):
        """Test getting user profile"""
        response = await client.get("/api/profiles/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["personal_info"]["full_name"] == test_profile["personal_info"]["full_name"]
        assert len(data["education"]) > 0
        assert len(data["experience"]) > 0
    
    @pytest.mark.asyncio
    async def test_get_profile_not_found(self, client: AsyncClient, auth_headers):
        """Test getting profile that doesn't exist"""
        response = await client.get("/api/profiles/me", headers=auth_headers)
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_update_profile(self, client: AsyncClient, auth_headers, test_profile):
        """Test updating profile"""
        update_data = {
            "full_name": "Updated Name",
            "phone": "+9876543210"
        }
        response = await client.put("/api/profiles/me", json=update_data, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["personal_info"]["full_name"] == update_data["full_name"]
        assert data["personal_info"]["phone"] == update_data["phone"]
    
    @pytest.mark.asyncio
    async def test_get_profile_completeness(self, client: AsyncClient, auth_headers, test_profile):
        """Test profile completeness calculation"""
        response = await client.get("/api/profiles/completeness", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "score" in data
        assert 0 <= data["score"] <= 100
        assert "missing_sections" in data
    
    @pytest.mark.asyncio
    async def test_profile_unauthorized(self, client: AsyncClient):
        """Test accessing profile without authentication"""
        response = await client.get("/api/profiles/me")
        assert response.status_code == 403
