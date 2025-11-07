#!/usr/bin/env python3
"""
Quick test script to verify profile update functionality
"""
import requests
import json

BASE_URL = "http://localhost:8001"

def test_profile_flow():
    print("Testing Profile Update Flow...")
    print("-" * 50)
    
    # 1. Register a test user
    print("\n1. Registering test user...")
    register_data = {
        "full_name": "Test User",
        "email": f"test_{int(time.time())}@example.com",
        "password": "testpass123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)
        if response.status_code == 201:
            print("✓ User registered successfully")
            token_data = response.json()
            print(f"  Token data: {token_data}")
            access_token = token_data.get("access_token")
        else:
            # User might exist, try login
            print("User might exist, trying login...")
            login_data = {
                "email": "test@example.com",
                "password": "testpass123"
            }
            response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
            if response.status_code == 200:
                token_data = response.json()
                access_token = token_data.get("access_token")
                print("✓ Logged in successfully")
            else:
                print(f"✗ Login failed: {response.text}")
                return
    except Exception as e:
        print(f"✗ Registration/Login error: {e}")
        return
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # 2. Create profile
    print("\n2. Creating profile...")
    profile_data = {
        "full_name": "Test User",
        "email": "test@example.com",
        "phone": "+1234567890",
        "location": "San Francisco, CA",
        "title": "Software Engineer"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/profiles/me", json=profile_data, headers=headers)
        if response.status_code in [201, 400]:  # 400 if already exists
            print("✓ Profile created or already exists")
        else:
            print(f"✗ Profile creation failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"✗ Profile creation error: {e}")
    
    # 3. Update profile with experience and education
    print("\n3. Updating profile with experience and education...")
    update_data = {
        "personal_info": {
            "full_name": "Test User",
            "email": "test@example.com",
            "phone": "+1234567890",
            "location": "San Francisco, CA",
            "title": "Senior Software Engineer"
        },
        "experience": [
            {
                "id": "exp-1",
                "company": "Google",
                "title": "Software Engineer",
                "employment_type": "Full-time",
                "start_date": "2020-01-01",
                "end_date": None,
                "is_current": True,
                "location": "Mountain View, CA",
                "responsibilities": ["Build scalable systems"],
                "achievements": ["Improved performance by 50%"],
                "technologies": ["Python", "Go"]
            }
        ],
        "education": [
            {
                "id": "edu-1",
                "institution": "Stanford University",
                "degree": "BS",
                "field": "Computer Science",
                "start_date": None,
                "end_date": None,
                "gpa": 3.8,
                "achievements": []
            }
        ],
        "skills": {
            "technical": [
                {"name": "Python", "level": "Expert"},
                {"name": "JavaScript", "level": "Advanced"}
            ],
            "soft": ["Leadership", "Communication"],
            "languages": [],
            "tools": []
        },
        "projects": [],
        "certifications": []
    }
    
    try:
        response = requests.put(f"{BASE_URL}/api/profiles/me", json=update_data, headers=headers)
        if response.status_code == 200:
            print("✓ Profile updated successfully")
            profile = response.json()
            print(f"  - Name: {profile.get('personal_info', {}).get('full_name')}")
            print(f"  - Experiences: {len(profile.get('experience', []))}")
            print(f"  - Education: {len(profile.get('education', []))}")
            print(f"  - Technical Skills: {len(profile.get('skills', {}).get('technical', []))}")
        else:
            print(f"✗ Profile update failed: {response.status_code}")
            print(f"  Response: {response.text}")
    except Exception as e:
        print(f"✗ Profile update error: {e}")
    
    # 4. Get profile
    print("\n4. Fetching updated profile...")
    try:
        response = requests.get(f"{BASE_URL}/api/profiles/me", headers=headers)
        if response.status_code == 200:
            print("✓ Profile fetched successfully")
            profile = response.json()
            print(f"  - Completeness Score: {profile.get('completeness_score', 0)}%")
        else:
            print(f"✗ Profile fetch failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"✗ Profile fetch error: {e}")
    
    print("\n" + "=" * 50)
    print("Test completed!")


if __name__ == "__main__":
    import time
    test_profile_flow()
