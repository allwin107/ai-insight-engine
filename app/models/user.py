"""
User Model
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from datetime import datetime
from app.database import Base

class User(Base):
    """User database model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    upload_count = Column(Integer, default=0)
    upload_limit = Column(Integer, default=10)  # Per month
    
    def __repr__(self):
        return f"<User {self.email}>"