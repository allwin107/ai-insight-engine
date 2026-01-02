"""
Data Processing API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime
import os

from app.database import get_db
from app.models.user import User
from app.models.job import Job
from app.auth.security import get_current_user
from app.services.cleaner import DataCleaner
from app.utils.helpers import get_upload_path, get_job_directory
from app.utils.logging import logger

router = APIRouter(prefix="/api/v1", tags=["Processing"])

def process_job_background(job_id: str, filepath: str, user_id: int):
    """
    Background task to process a job
    
    This runs asynchronously after file upload
    """
    from app.database import SessionLocal
    
    db = SessionLocal()
    
    try:
        # Get job from database
        job = db.query(Job).filter(Job.job_id == job_id).first()
        if not job:
            logger.error("job_not_found", job_id=job_id)
            return
        
        # Update job status
        job.status = "processing"
        job.started_at = datetime.utcnow()
        db.commit()
        
        logger.info("processing_started", job_id=job_id, filepath=filepath)
        
        # Initialize cleaner
        cleaner = DataCleaner()
        
        # Run cleaning pipeline
        result = cleaner.clean(filepath)
        
        # Update job with results
        job.status = "complete"
        job.progress = 100
        job.rows_count = len(result['cleaned_df'])
        job.quality_score = int(result['quality_score'])
        job.completed_at = datetime.utcnow()
        job.processing_time = (job.completed_at - job.started_at).total_seconds()
        
        # Save cleaned data
        cleaned_path = os.path.join(get_job_directory(job_id), 'cleaned_data.csv')
        result['cleaned_df'].to_csv(cleaned_path, index=False)
        
        # Save cleaning log
        log_path = os.path.join(get_job_directory(job_id), 'cleaning_log.txt')
        with open(log_path, 'w') as f:
            f.write('\n'.join(result['cleaning_log']))
        
        db.commit()
        
        logger.info("processing_complete", 
                   job_id=job_id, 
                   quality_score=job.quality_score,
                   processing_time=job.processing_time)
        
    except Exception as e:
        logger.error("processing_failed", job_id=job_id, error=str(e))
        
        # Update job with error
        job = db.query(Job).filter(Job.job_id == job_id).first()
        if job:
            job.status = "failed"
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            db.commit()
    
    finally:
        db.close()

@router.post("/process/{job_id}")
async def start_processing(
    job_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Start processing a job
    
    This triggers the data cleaning pipeline in the background.
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
    
    # Check if already processing or complete
    if job.status in ["processing", "complete"]:
        return {
            "message": f"Job is already {job.status}",
            "job_id": job_id,
            "status": job.status
        }
    
    # Get file path
    filepath = get_upload_path(job_id, job.filename)
    
    if not os.path.exists(filepath):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Uploaded file not found"
        )
    
    # Add to background tasks
    background_tasks.add_task(
        process_job_background,
        job_id=job_id,
        filepath=filepath,
        user_id=current_user.id
    )
    
    return {
        "message": "Processing started",
        "job_id": job_id,
        "status": "processing"
    }

@router.get("/results/{job_id}")
async def get_results(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get processing results for a completed job
    
    Returns cleaned data summary and cleaning log
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
    
    # Check if complete
    if job.status != "complete":
        return {
            "job_id": job_id,
            "status": job.status,
            "message": f"Job is {job.status}. Results not available yet."
        }
    
    # Load cleaning log
    log_path = os.path.join(get_job_directory(job_id), 'cleaning_log.txt')
    cleaning_log = []
    if os.path.exists(log_path):
        with open(log_path, 'r') as f:
            cleaning_log = f.read().split('\n')
    
    # Load cleaned data (just metadata, not full data)
    cleaned_path = os.path.join(get_job_directory(job_id), 'cleaned_data.csv')
    data_preview = None
    if os.path.exists(cleaned_path):
        import pandas as pd
        df = pd.read_csv(cleaned_path, nrows=5)  # Just first 5 rows
        data_preview = df.to_dict('records')
    
    return {
        "job_id": job_id,
        "status": job.status,
        "quality_score": job.quality_score,
        "rows_count": job.rows_count,
        "processing_time": job.processing_time,
        "cleaning_log": cleaning_log,
        "data_preview": data_preview,
        "files": {
            "cleaned_data": f"/api/v1/download/{job_id}/cleaned_data.csv",
            "cleaning_log": f"/api/v1/download/{job_id}/cleaning_log.txt"
        }
    }

@router.get("/download/{job_id}/{filename}")
async def download_file(
    job_id: str,
    filename: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Download a file from a completed job
    
    Allows downloading cleaned data or cleaning log
    """
    from fastapi.responses import FileResponse
    
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
    
    # Get file path
    filepath = os.path.join(get_job_directory(job_id), filename)
    
    if not os.path.exists(filepath):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    return FileResponse(
        filepath,
        media_type='application/octet-stream',
        filename=filename
    )