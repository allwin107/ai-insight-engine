"""
File Upload API endpoints
"""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.models.user import User
from app.models.job import Job
from app.auth.security import get_current_user
from app.utils.validation import validate_upload_file, save_upload_file
from app.utils.helpers import generate_job_id, get_upload_path
from app.config import settings

router = APIRouter(prefix="/api/v1", tags=["Upload"])

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a CSV or Excel file for processing
    
    Requires authentication. Returns job_id for tracking.
    Automatically starts data cleaning in the background.
    """
    
    # Check upload limit
    if current_user.upload_count >= current_user.upload_limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Upload limit reached ({current_user.upload_limit}/month). Please upgrade."
        )
    
    # Validate file
    is_valid, error_message = validate_upload_file(file)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )
    
    # Generate job ID
    job_id = generate_job_id()
    
    # Save file
    filepath = get_upload_path(job_id, file.filename)
    file_size = await save_upload_file(file, filepath)
    
    # Create job record
    new_job = Job(
        job_id=job_id,
        user_id=current_user.id,
        filename=file.filename,
        file_size=file_size,
        status="queued",
        progress=0
    )
    
    db.add(new_job)
    
    # Update user upload count
    current_user.upload_count += 1
    
    db.commit()
    db.refresh(new_job)
    
    # Start processing in background
    from app.api.process import process_job_background
    background_tasks.add_task(
        process_job_background,
        job_id=job_id,
        filepath=filepath,
        user_id=current_user.id
    )
    
    return {
        "job_id": job_id,
        "filename": file.filename,
        "file_size": file_size,
        "status": "processing",
        "message": "File uploaded successfully. Processing started automatically.",
        "created_at": new_job.created_at.isoformat()
    }

@router.get("/jobs/{job_id}")
async def get_job_status(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get job status and progress
    
    Returns current processing status, progress, and results if complete.
    """
    
    # Find job
    job = db.query(Job).filter(Job.job_id == job_id).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Check ownership
    if job.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this job"
        )
    
    # Return job details
    return {
        "job_id": job.job_id,
        "filename": job.filename,
        "status": job.status,
        "progress": job.progress,
        "rows_count": job.rows_count,
        "quality_score": job.quality_score,
        "created_at": job.created_at.isoformat() if job.created_at else None,
        "started_at": job.started_at.isoformat() if job.started_at else None,
        "completed_at": job.completed_at.isoformat() if job.completed_at else None,
        "processing_time": job.processing_time,
        "error_message": job.error_message
    }

@router.get("/jobs")
async def list_user_jobs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 10,
    offset: int = 0
):
    """
    List all jobs for current user
    
    Returns paginated list of user's jobs.
    """
    
    jobs = db.query(Job)\
        .filter(Job.user_id == current_user.id)\
        .order_by(Job.created_at.desc())\
        .limit(limit)\
        .offset(offset)\
        .all()
    
    return {
        "jobs": [
            {
                "job_id": job.job_id,
                "filename": job.filename,
                "status": job.status,
                "progress": job.progress,
                "quality_score": job.quality_score,
                "created_at": job.created_at.isoformat() if job.created_at else None,
            }
            for job in jobs
        ],
        "total": db.query(Job).filter(Job.user_id == current_user.id).count(),
        "limit": limit,
        "offset": offset
    }

@router.delete("/jobs/{job_id}")
async def delete_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a job and its files
    
    Cancels processing if in progress and removes all associated data.
    """
    from app.utils.helpers import cleanup_job_files
    
    # Find job
    job = db.query(Job).filter(Job.job_id == job_id).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Check ownership
    if job.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this job"
        )
    
    # Delete files
    cleanup_job_files(job_id)
    
    # Delete database record
    db.delete(job)
    db.commit()
    
    return {
        "message": "Job deleted successfully",
        "job_id": job_id
    }