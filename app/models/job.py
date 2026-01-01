"""
Job Model - Tracks data processing jobs
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from datetime import datetime
from app.database import Base

class Job(Base):
    """Job database model"""
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # File info
    filename = Column(String, nullable=False)
    file_size = Column(Integer, nullable=True)  # bytes
    
    # Processing status
    status = Column(String, default="queued")  # queued, processing, complete, failed
    progress = Column(Integer, default=0)  # 0-100
    
    # Results
    rows_count = Column(Integer, nullable=True)
    quality_score = Column(Integer, nullable=True)  # 0-100
    
    # Timing
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    processing_time = Column(Float, nullable=True)  # seconds
    
    # Error handling
    error_message = Column(String, nullable=True)
    
    def __repr__(self):
        return f"<Job {self.job_id} - {self.status}>"