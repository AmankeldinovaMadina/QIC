"""Authentication service layer."""

import uuid
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.settings import settings
from app.db.models import User, UserSession
from app.auth.schemas import AuthResponse


class AuthService:
    """Authentication service for user registration and login."""

    async def register_user(self, session: AsyncSession, username: str) -> User:
        """Register a new user or return existing user."""
        # Check if user exists
        stmt = select(User).where(User.username == username)
        result = await session.execute(stmt)
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            return existing_user
        
        # Create new user
        user = User(username=username)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    async def login_user(self, session: AsyncSession, username: str) -> Optional[AuthResponse]:
        """Login user and create session token."""
        # Find user
        stmt = select(User).where(User.username == username)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            return None
        
        # Create session token
        token = str(uuid.uuid4())
        expires_at = datetime.utcnow() + timedelta(days=settings.access_token_expire_days)
        
        user_session = UserSession(
            user_id=user.id,
            token=token,
            expires_at=expires_at
        )
        
        session.add(user_session)
        await session.commit()
        
        return AuthResponse(
            access_token=token,
            expires_at=expires_at,
            user_id=user.id,  # This is now a string
            username=user.username
        )

    async def get_user_by_token(self, session: AsyncSession, token: str) -> Optional[User]:
        """Get user by session token."""
        stmt = (
            select(User)
            .join(UserSession)
            .where(
                UserSession.token == token,
                UserSession.expires_at > datetime.utcnow()
            )
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def logout_user(self, session: AsyncSession, token: str) -> bool:
        """Logout user by invalidating session token."""
        stmt = select(UserSession).where(UserSession.token == token)
        result = await session.execute(stmt)
        user_session = result.scalar_one_or_none()
        
        if user_session:
            await session.delete(user_session)
            await session.commit()
            return True
        
        return False


# Global service instance
auth_service = AuthService()