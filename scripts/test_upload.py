"""
Test script for file upload functionality
Run this after starting the backend and creating a user
"""
import requests
import io

API_URL = "http://localhost:8000"

def login_and_get_token():
    """Login and get access token"""
    print("\n🔐 Logging in...")
    
    response = requests.post(
        f"{API_URL}/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )
    
    if response.status_code == 200:
        token = response.json()['access_token']
        print("✅ Login successful!")
        return token
    else:
        print("❌ Login failed. Make sure you've registered first.")
        return None

def create_sample_csv():
    """Create a sample CSV file for testing"""
    csv_data = """Date,Product,Sales,Quantity,Region
2024-01-01,Product A,1200,50,North
2024-01-02,Product B,800,30,South
2024-01-03,Product A,1500,60,East
2024-01-04,Product C,950,40,West
2024-01-05,Product B,1100,45,North
2024-01-06,Product A,1300,55,South
2024-01-07,Product C,900,35,East
2024-01-08,Product B,1000,42,West
2024-01-09,Product A,1400,58,North
2024-01-10,Product C,850,33,South"""
    
    return io.BytesIO(csv_data.encode('utf-8'))

def test_upload(token):
    """Test file upload"""
    print("\n📤 Testing file upload...")
    
    # Create sample CSV
    csv_file = create_sample_csv()
    
    # Prepare files
    files = {
        'file': ('sales_data.csv', csv_file, 'text/csv')
    }
    
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    response = requests.post(
        f"{API_URL}/api/v1/upload",
        files=files,
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Upload successful!")
        print(f"   Job ID: {data['job_id']}")
        print(f"   Filename: {data['filename']}")
        print(f"   Status: {data['status']}")
        return data['job_id']
    else:
        print(f"❌ Upload failed: {response.json()}")
        return None

def test_get_job_status(token, job_id):
    """Test getting job status"""
    print(f"\n🔍 Getting job status for {job_id}...")
    
    headers = {'Authorization': f'Bearer {token}'}
    
    response = requests.get(
        f"{API_URL}/api/v1/jobs/{job_id}",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Job status retrieved!")
        print(f"   Filename: {data['filename']}")
        print(f"   Status: {data['status']}")
        print(f"   Progress: {data['progress']}%")
    else:
        print(f"❌ Failed to get status: {response.json()}")

def test_list_jobs(token):
    """Test listing all jobs"""
    print("\n📋 Listing all jobs...")
    
    headers = {'Authorization': f'Bearer {token}'}
    
    response = requests.get(
        f"{API_URL}/api/v1/jobs",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Found {data['total']} jobs")
        for job in data['jobs']:
            print(f"   • {job['filename']} - {job['status']}")
    else:
        print(f"❌ Failed to list jobs: {response.json()}")

def test_invalid_file(token):
    """Test uploading invalid file"""
    print("\n🧪 Testing invalid file upload...")
    
    # Create a fake PDF file (should fail validation)
    fake_pdf = io.BytesIO(b"Not a real PDF file")
    
    files = {
        'file': ('fake.pdf', fake_pdf, 'application/pdf')
    }
    
    headers = {'Authorization': f'Bearer {token}'}
    
    response = requests.post(
        f"{API_URL}/api/v1/upload",
        files=files,
        headers=headers
    )
    
    if response.status_code == 400:
        print("✅ Invalid file correctly rejected!")
        print(f"   Error: {response.json()['detail']}")
    else:
        print(f"⚠️ Unexpected response: {response.status_code}")

def test_large_file(token):
    """Test uploading file that's too large"""
    print("\n🧪 Testing oversized file upload...")
    
    # Create a 15MB file (exceeds 10MB limit)
    large_data = "x" * (15 * 1024 * 1024)
    large_file = io.BytesIO(large_data.encode('utf-8'))
    
    files = {
        'file': ('large.csv', large_file, 'text/csv')
    }
    
    headers = {'Authorization': f'Bearer {token}'}
    
    response = requests.post(
        f"{API_URL}/api/v1/upload",
        files=files,
        headers=headers
    )
    
    if response.status_code == 400:
        print("✅ Large file correctly rejected!")
        print(f"   Error: {response.json()['detail']}")
    else:
        print(f"⚠️ Unexpected response: {response.status_code}")

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 AI Data Insight Engine - Upload Tests")
    print("=" * 60)
    
    # Login
    token = login_and_get_token()
    
    if not token:
        print("\n❌ Can't proceed without token.")
        print("Make sure you've registered a user first:")
        print("  python scripts/test_auth.py")
        exit(1)
    
    # Test valid upload
    job_id = test_upload(token)
    
    if job_id:
        # Test get job status
        test_get_job_status(token, job_id)
        
        # Test list jobs
        test_list_jobs(token)
    
    # Test invalid uploads
    test_invalid_file(token)
    test_large_file(token)
    
    print("\n" + "=" * 60)
    print("✨ Tests Complete!")
    print("=" * 60)
    print("\n💡 Next: Try uploading via the frontend!")
    print("   http://localhost:8501")