"""Authentication schemas and DTOs."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class UserRegisterRequest(BaseModel):
    """User registration request."""
    username: str = Field(..., min_length=3, max_length=50)


class UserLoginRequest(BaseModel):
    """User login request."""
    username: str = Field(..., min_length=3, max_length=50)


class AuthResponse(BaseModel):
    """Authentication response."""
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime
    user_id: str  # Changed from UUID to str
    username: str


class UserResponse(BaseModel):
    """User response model."""
    id: str  # Changed from UUID to str
    username: str
    created_at: datetime

    class Config:
        from_attributes = True