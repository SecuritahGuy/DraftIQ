"""
Yahoo OAuth service for handling authentication flow.
"""

import secrets
import httpx
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional
from urllib.parse import urlencode
from app.core.config import settings


class YahooOAuthService:
    """Yahoo OAuth service for handling authentication."""
    
    def __init__(self):
        self.client_id = settings.yahoo_client_id
        self.client_secret = settings.yahoo_client_secret
        self.redirect_uri = settings.yahoo_redirect_uri
        self.auth_url = "https://api.login.yahoo.com/oauth2/request_auth"
        self.token_url = "https://api.login.yahoo.com/oauth2/get_token"
    
    def generate_state(self) -> str:
        """Generate a random state parameter for OAuth security."""
        return secrets.token_urlsafe(32)
    
    def get_authorization_url(self, state: str) -> str:
        """
        Generate Yahoo OAuth authorization URL.
        
        Args:
            state: OAuth state parameter for security
            
        Returns:
            Authorization URL for Yahoo OAuth
        """
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "state": state,
            "scope": "fspt-r"  # Fantasy Sports Read/Write
        }
        return f"{self.auth_url}?{urlencode(params)}"
    
    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from Yahoo OAuth callback
            
        Returns:
            Token response from Yahoo
            
        Raises:
            httpx.HTTPStatusError: If the token exchange fails
        """
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(self.token_url, data=data)
            response.raise_for_status()
            return response.json()
    
    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh access token using refresh token.
        
        Args:
            refresh_token: Refresh token from previous OAuth flow
            
        Returns:
            New token response from Yahoo
            
        Raises:
            httpx.HTTPStatusError: If the token refresh fails
        """
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(self.token_url, data=data)
            response.raise_for_status()
            return response.json()
    
    def parse_token_response(self, token_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse and validate token response from Yahoo.
        
        Args:
            token_data: Raw token response from Yahoo
            
        Returns:
            Parsed token data with calculated expiration
        """
        # Check for error response
        if "error" in token_data:
            error_msg = token_data.get("error_description", token_data["error"])
            raise Exception(f"OAuth error: {error_msg}")
        
        expires_in = token_data.get("expires_in", 3600)  # Default to 1 hour
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
        
        return {
            "access_token": token_data["access_token"],
            "refresh_token": token_data.get("refresh_token"),
            "expires_at": expires_at,
            "token_type": token_data.get("token_type", "Bearer"),
            "scope": token_data.get("scope"),
            "expires_in": expires_in
        }
