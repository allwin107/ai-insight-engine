"""
Test script for authentication endpoints
Run this after starting the backend
"""
import requests
import json

API_URL = "http://localhost:8000"

def test_register():
    """Test user registration"""
    print("\n🧪 Testing User Registration...")
    
    response = requests.post(
        f"{API_URL}/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "testpassword123",
            "full_name": "Test User"
        }
    )
    
    if response.status_code == 201:
        print("✅ Registration successful!")
        data = response.json()
        print(f"   User: {data['user']['email']}")
        print(f"   Token: {data['access_token'][:50]}...")
        return data['access_token']
    else:
        print(f"❌ Registration failed: {response.json()}")
        return None

def test_login():
    """Test user login"""
    print("\n🧪 Testing User Login...")
    
    response = requests.post(
        f"{API_URL}/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )
    
    if response.status_code == 200:
        print("✅ Login successful!")
        data = response.json()
        print(f"   User: {data['user']['email']}")
        print(f"   Token: {data['access_token'][:50]}...")
        return data['access_token']
    else:
        print(f"❌ Login failed: {response.json()}")
        return None

def test_get_me(token):
    """Test getting current user info"""
    print("\n🧪 Testing Get Current User...")
    
    response = requests.get(
        f"{API_URL}/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        print("✅ Get user successful!")
        data = response.json()
        print(f"   Email: {data['email']}")
        print(f"   Name: {data['full_name']}")
        print(f"   Upload Count: {data['upload_count']}/{data['upload_limit']}")
    else:
        print(f"❌ Get user failed: {response.json()}")

def test_invalid_token():
    """Test with invalid token"""
    print("\n🧪 Testing Invalid Token...")
    
    response = requests.get(
        f"{API_URL}/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid_token_xyz"}
    )
    
    if response.status_code == 401:
        print("✅ Invalid token correctly rejected!")
    else:
        print(f"⚠️ Unexpected response: {response.status_code}")

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 AI Data Insight Engine - Authentication Tests")
    print("=" * 60)
    
    # Test registration
    token = test_register()
    
    if token:
        # Test get current user
        test_get_me(token)
        
        # Test login
        login_token = test_login()
        
        if login_token:
            test_get_me(login_token)
    
    # Test invalid token
    test_invalid_token()
    
    print("\n" + "=" * 60)
    print("✨ Tests Complete!")
    print("=" * 60)