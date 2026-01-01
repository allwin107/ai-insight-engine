"""
Helper utilities
"""
import uuid
import os
from datetime import datetime

def generate_job_id() -> str:
    """Generate unique job ID"""
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    return f"{timestamp}_{unique_id}"

def get_upload_path(job_id: str, filename: str) -> str:
    """Get full path for uploaded file"""
    from app.config import settings
    
    # Ensure upload directory exists
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    # Create job-specific directory
    job_dir = os.path.join(settings.UPLOAD_DIR, job_id)
    os.makedirs(job_dir, exist_ok=True)
    
    # Return full filepath
    return os.path.join(job_dir, filename)

def get_job_directory(job_id: str) -> str:
    """Get job directory path"""
    from app.config import settings
    return os.path.join(settings.UPLOAD_DIR, job_id)

def cleanup_job_files(job_id: str):
    """Delete all files for a job"""
    import shutil
    job_dir = get_job_directory(job_id)
    if os.path.exists(job_dir):
        try:
            shutil.rmtree(job_dir)
        except Exception as e:
            print(f"Failed to cleanup job {job_id}: {e}")