"""
Pydantic schemas for authentication and OAuth.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class OAuthStartRequest(BaseModel):
    """Request to start OAuth flow."""
    
    redirect_after_auth: Optional[str] = Field(
        default=None,
        description="URL to redirect to after successful authentication"
    )


class OAuthStartResponse(BaseModel):
    """Response for OAuth start."""
    
    authorization_url: str = Field(..., description="Yahoo OAuth authorization URL")
    state: str = Field(..., description="OAuth state parameter for security")
    
    class Config:
        json_schema_extra = {
            "example": {
                "authorization_url": "https://api.login.yahoo.com/oauth2/request_auth?client_id=...",
                "state": "abc123def456..."
            }
        }


class OAuthCallbackRequest(BaseModel):
    """OAuth callback parameters."""
    
    code: str = Field(..., description="Authorization code from Yahoo")
    state: str = Field(..., description="OAuth state parameter for verification")


class OAuthCallbackResponse(BaseModel):
    """Response for OAuth callback."""
    
    success: bool = Field(..., description="Whether authentication was successful")
    user_id: Optional[str] = Field(default=None, description="User ID if authentication successful")
    message: str = Field(..., description="Response message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "user_id": "user_123",
                "message": "Authentication successful"
            }
        }


class TokenInfo(BaseModel):
    """Token information."""
    
    access_token: str = Field(..., description="Access token")
    refresh_token: Optional[str] = Field(default=None, description="Refresh token")
    expires_at: datetime = Field(..., description="Token expiration time")
    token_type: str = Field(default="Bearer", description="Token type")
    scope: Optional[str] = Field(default=None, description="Token scope")


class UserInfo(BaseModel):
    """User information."""
    
    id: str = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    username: str = Field(..., description="Username")
    display_name: Optional[str] = Field(default=None, description="Display name")
    is_active: bool = Field(default=True, description="Whether user is active")
    is_verified: bool = Field(default=False, description="Whether user is verified")
    created_at: datetime = Field(..., description="User creation time")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "user_123",
                "email": "user@example.com",
                "username": "fantasyuser",
                "display_name": "Fantasy User",
                "is_active": True,
                "is_verified": True,
                "created_at": "2024-01-01T00:00:00Z"
            }
        }


class AuthError(BaseModel):
    """Authentication error response."""
    
    error: str = Field(..., description="Error type")
    error_description: str = Field(..., description="Error description")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "invalid_grant",
                "error_description": "The authorization code is invalid or expired"
            }
        }
