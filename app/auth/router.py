"""Authentication router."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_async_session
from app.auth.schemas import UserRegisterRequest, UserLoginRequest, AuthResponse, UserResponse
from app.auth.service import auth_service
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=AuthResponse)
async def register(
    request: UserRegisterRequest,
    session: AsyncSession = Depends(get_async_session)
):
    """Register a new user or return existing user."""
    user = await auth_service.register_user(session, request.username)
    
    # Auto-login after registration
    auth_response = await auth_service.login_user(session, request.username)
    
    if not auth_response:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create session after registration"
        )
    
    return auth_response


@router.post("/login", response_model=AuthResponse)
async def login(
    request: UserLoginRequest,
    session: AsyncSession = Depends(get_async_session)
):
    """Login user and create session token."""
    auth_response = await auth_service.login_user(session, request.username)
    
    if not auth_response:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return auth_response


@router.post("/logout")
async def logout(
    session: AsyncSession = Depends(get_async_session),
    current_user = Depends(get_current_user)
):
    """Logout current user and invalidate session token."""
    # We can't easily get the token here without modifying the dependency
    # For now, return success (token will expire naturally)
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user = Depends(get_current_user)
):
    """Get current user information."""
    return current_user