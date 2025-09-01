"""
User model for authentication and OAuth token storage.
"""

from datetime import datetime, timedelta
from typing import List
from sqlalchemy import String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class User(BaseModel):
    """User model for authentication."""
    
    __tablename__ = "users"
    
    # User identification
    id: Mapped[str] = mapped_column(String, primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    
    # User status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Profile information
    display_name: Mapped[str] = mapped_column(String, nullable=True)
    
    # Relationships
    yahoo_tokens: Mapped[List["YahooToken"]] = relationship("YahooToken", back_populates="user")
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, username={self.username})>"


class YahooToken(BaseModel):
    """Yahoo OAuth token storage."""
    
    __tablename__ = "yahoo_tokens"
    
    # Token identification
    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False, index=True)
    
    # OAuth tokens
    access_token: Mapped[str] = mapped_column(String, nullable=False)
    refresh_token: Mapped[str] = mapped_column(String, nullable=False)
    
    # Token metadata
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    token_type: Mapped[str] = mapped_column(String, default="Bearer", nullable=False)
    scope: Mapped[str] = mapped_column(String, nullable=True)
    
    # Yahoo user info
    yahoo_user_id: Mapped[str] = mapped_column(String, nullable=True)
    yahoo_guid: Mapped[str] = mapped_column(String, nullable=True)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="yahoo_tokens")
    
    def __repr__(self) -> str:
        return f"<YahooToken(user_id={self.user_id}, expires_at={self.expires_at})>"
    
    @property
    def is_expired(self) -> bool:
        """Check if the access token is expired."""
        return datetime.utcnow() >= self.expires_at
    
    @property
    def needs_refresh(self) -> bool:
        """Check if the token needs to be refreshed (5-minute buffer)."""
        return datetime.utcnow() >= (self.expires_at - timedelta(minutes=5))
