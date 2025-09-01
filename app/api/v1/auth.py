"""
OAuth authentication endpoints for Yahoo Fantasy API.
"""

import secrets
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.yahoo_oauth import YahooOAuthService
from app.schemas.auth import (
    OAuthStartRequest,
    OAuthStartResponse,
    OAuthCallbackResponse,
    AuthError
)

router = APIRouter(prefix="/auth", tags=["authentication"])

# In-memory storage for OAuth state (in production, use Redis or database)
oauth_states: Dict[str, Dict[str, Any]] = {}


@router.post("/yahoo/start", response_model=OAuthStartResponse)
async def start_yahoo_oauth(
    request: OAuthStartRequest,
    oauth_service: YahooOAuthService = Depends(lambda: YahooOAuthService())
) -> OAuthStartResponse:
    """
    Start Yahoo OAuth flow.
    
    This endpoint generates an authorization URL that the user should visit
    to authenticate with Yahoo Fantasy Sports.
    """
    # Generate OAuth state for security
    state = oauth_service.generate_state()
    
    # Store state information (in production, use Redis or database)
    oauth_states[state] = {
        "redirect_after_auth": request.redirect_after_auth,
        "created_at": "2024-01-01T00:00:00Z"  # In production, use actual timestamp
    }
    
    # Generate authorization URL
    authorization_url = oauth_service.get_authorization_url(state)
    
    return OAuthStartResponse(
        authorization_url=authorization_url,
        state=state
    )


@router.get("/yahoo/callback")
async def yahoo_oauth_callback(
    code: str = Query(..., description="Authorization code from Yahoo"),
    state: str = Query(..., description="OAuth state parameter"),
    db: AsyncSession = Depends(get_db),
    oauth_service: YahooOAuthService = Depends(lambda: YahooOAuthService())
) -> OAuthCallbackResponse:
    """
    Handle Yahoo OAuth callback.
    
    This endpoint is called by Yahoo after the user authorizes the application.
    It exchanges the authorization code for access tokens and creates/updates
    the user account.
    """
    try:
        # Validate OAuth state
        if state not in oauth_states:
            raise HTTPException(
                status_code=400,
                detail="Invalid OAuth state parameter"
            )
        
        # Exchange authorization code for tokens
        token_data = await oauth_service.exchange_code_for_token(code)
        parsed_tokens = oauth_service.parse_token_response(token_data)
        
        # TODO: Create or update user in database
        # TODO: Store tokens in database
        # TODO: Get Yahoo user information
        
        # For now, return a simple success response
        # In production, this would create/update the user and tokens
        
        # Clean up OAuth state
        oauth_states.pop(state, None)
        
        return OAuthCallbackResponse(
            success=True,
            user_id="temp_user_id",  # TODO: Use actual user ID
            message="Authentication successful"
        )
        
    except Exception as e:
        # Clean up OAuth state on error
        oauth_states.pop(state, None)
        
        raise HTTPException(
            status_code=400,
            detail=f"OAuth callback failed: {str(e)}"
        )


@router.get("/yahoo/authorize")
async def yahoo_oauth_authorize(
    request: Request,
    oauth_service: YahooOAuthService = Depends(lambda: YahooOAuthService())
) -> RedirectResponse:
    """
    Redirect to Yahoo OAuth authorization page.
    
    This is a convenience endpoint that directly redirects users to Yahoo's
    authorization page without requiring a POST request.
    """
    # Generate OAuth state
    state = oauth_service.generate_state()
    
    # Store state information
    oauth_states[state] = {
        "redirect_after_auth": str(request.query_params.get("redirect_after_auth", "")),
        "created_at": "2024-01-01T00:00:00Z"  # In production, use actual timestamp
    }
    
    # Generate and redirect to authorization URL
    authorization_url = oauth_service.get_authorization_url(state)
    return RedirectResponse(url=authorization_url)


@router.get("/status")
async def auth_status() -> Dict[str, Any]:
    """
    Get authentication status.
    
    This endpoint returns information about the current authentication state.
    For development, we'll return authenticated=True since credentials are configured.
    """
    return {
        "authenticated": True,  # Development mode - credentials configured in .env
        "user": {
            "id": "dev_user",
            "email": "dev@draftiq.local",
            "username": "dev_user",
            "display_name": "Development User",
            "is_active": True,
            "is_verified": True,
            "created_at": "2024-01-01T00:00:00Z"
        },
        "yahoo_token": {
            "id": "dev_token",
            "user_id": "dev_user",
            "access_token": "dev_access_token",
            "refresh_token": "dev_refresh_token",
            "expires_at": "2025-12-31T23:59:59Z",
            "token_type": "Bearer",
            "scope": "openid",
            "created_at": "2024-01-01T00:00:00Z"
        },
        "message": "Development mode - using configured credentials"
    }
