"""
Pydantic schemas for authentication
"""
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

# Request schemas
class UserRegister(BaseModel):
    """User registration request"""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    """User login request"""
    email: EmailStr
    password: str

# Response schemas
class UserResponse(BaseModel):
    """User response (without password)"""
    id: int
    email: str
    full_name: Optional[str]
    is_active: bool
    created_at: datetime
    upload_count: int
    upload_limit: int
    
    class Config:
        from_attributes = True  # For Pydantic v2

class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class TokenData(BaseModel):
    """Token payload data"""
    user_id: int
    email: str