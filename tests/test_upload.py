"""
Tests for file upload functionality
"""
import pytest
import io
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(scope="function", autouse=True)
def setup_database():
    """Create tables before each test"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def auth_token():
    """Get authentication token"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "password123",
            "full_name": "Test User"
        }
    )
    return response.json()["access_token"]

@pytest.fixture
def sample_csv():
    """Create sample CSV file"""
    csv_data = """Date,Product,Sales
2024-01-01,Product A,1200
2024-01-02,Product B,800
2024-01-03,Product C,950"""
    return io.BytesIO(csv_data.encode('utf-8'))

@pytest.mark.upload
class TestFileUpload:
    """Test file upload functionality"""
    
    def test_upload_success(self, auth_token, sample_csv):
        """Test successful file upload"""
        files = {'file': ('sales.csv', sample_csv, 'text/csv')}
        headers = {'Authorization': f'Bearer {auth_token}'}
        
        response = client.post(
            "/api/v1/upload",
            files=files,
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        assert data["filename"] == "sales.csv"
        assert data["status"] == "queued"
    
    def test_upload_unauthenticated(self, sample_csv):
        """Test upload without authentication"""
        files = {'file': ('sales.csv', sample_csv, 'text/csv')}
        
        response = client.post("/api/v1/upload", files=files)
        assert response.status_code == 403
    
    def test_upload_invalid_file_type(self, auth_token):
        """Test upload with invalid file type"""
        fake_pdf = io.BytesIO(b"Not a real file")
        files = {'file': ('document.pdf', fake_pdf, 'application/pdf')}
        headers = {'Authorization': f'Bearer {auth_token}'}
        
        response = client.post(
            "/api/v1/upload",
            files=files,
            headers=headers
        )
        
        assert response.status_code == 400
        assert "not allowed" in response.json()["detail"].lower()
    
    def test_upload_too_large(self, auth_token):
        """Test upload with oversized file"""
        # Create 15MB file (exceeds 10MB limit)
        large_data = "x" * (15 * 1024 * 1024)
        large_file = io.BytesIO(large_data.encode('utf-8'))
        files = {'file': ('large.csv', large_file, 'text/csv')}
        headers = {'Authorization': f'Bearer {auth_token}'}
        
        response = client.post(
            "/api/v1/upload",
            files=files,
            headers=headers
        )
        
        assert response.status_code == 400
        assert "too large" in response.json()["detail"].lower()
    
    def test_get_job_status(self, auth_token, sample_csv):
        """Test getting job status"""
        # Upload file
        files = {'file': ('sales.csv', sample_csv, 'text/csv')}
        headers = {'Authorization': f'Bearer {auth_token}'}
        
        upload_response = client.post(
            "/api/v1/upload",
            files=files,
            headers=headers
        )
        job_id = upload_response.json()["job_id"]
        
        # Get job status
        response = client.get(
            f"/api/v1/jobs/{job_id}",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["job_id"] == job_id
        assert data["status"] == "queued"
    
    def test_list_jobs(self, auth_token, sample_csv):
        """Test listing user jobs"""
        # Upload multiple files
        headers = {'Authorization': f'Bearer {auth_token}'}
        
        for i in range(3):
            files = {'file': (f'file{i}.csv', sample_csv, 'text/csv')}
            client.post("/api/v1/upload", files=files, headers=headers)
            sample_csv.seek(0)  # Reset file pointer
        
        # List jobs
        response = client.get("/api/v1/jobs", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert len(data["jobs"]) == 3
    
    def test_delete_job(self, auth_token, sample_csv):
        """Test deleting a job"""
        # Upload file
        files = {'file': ('sales.csv', sample_csv, 'text/csv')}
        headers = {'Authorization': f'Bearer {auth_token}'}
        
        upload_response = client.post(
            "/api/v1/upload",
            files=files,
            headers=headers
        )
        job_id = upload_response.json()["job_id"]
        
        # Delete job
        response = client.delete(
            f"/api/v1/jobs/{job_id}",
            headers=headers
        )
        
        assert response.status_code == 200
        
        # Verify job is deleted
        get_response = client.get(
            f"/api/v1/jobs/{job_id}",
            headers=headers
        )
        assert get_response.status_code == 404