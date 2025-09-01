"""
Yahoo Fantasy API client service for league and team data synchronization.
"""

import httpx
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.core.config import settings
from app.services.yahoo_oauth import YahooOAuthService


class YahooAPIClient:
    """Yahoo Fantasy API client for data synchronization."""
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://fantasysports.yahooapis.com/fantasy/v2"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
    
    async def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make a request to the Yahoo Fantasy API.
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            
        Returns:
            API response data
            
        Raises:
            httpx.HTTPStatusError: If the API request fails
        """
        url = f"{self.base_url}/{endpoint}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
    
    async def get_user_leagues(self) -> List[Dict[str, Any]]:
        """
        Get all leagues for the authenticated user.
        
        Returns:
            List of user's leagues
        """
        response = await self._make_request("users;use_login=1/games;game_keys=nfl/leagues")
        
        # Parse the response to extract leagues
        leagues = []
        if "fantasy_content" in response:
            user_data = response["fantasy_content"]["users"]["0"]["user"]
            if "games" in user_data:
                for game in user_data["games"].values():
                    if isinstance(game, dict) and "leagues" in game:
                        for league in game["leagues"].values():
                            if isinstance(league, dict) and "league" in league:
                                leagues.append(league["league"])
        
        return leagues
    
    async def get_league_details(self, league_key: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific league.
        
        Args:
            league_key: Yahoo league key
            
        Returns:
            League details including settings, teams, and scoring
        """
        response = await self._make_request(f"league/{league_key}")
        
        if "fantasy_content" in response:
            return response["fantasy_content"]["league"]["0"]
        
        raise ValueError("Invalid league response format")
    
    async def get_league_teams(self, league_key: str) -> List[Dict[str, Any]]:
        """
        Get all teams in a league.
        
        Args:
            league_key: Yahoo league key
            
        Returns:
            List of teams in the league
        """
        response = await self._make_request(f"league/{league_key}/teams")
        
        teams = []
        if "fantasy_content" in response:
            league_data = response["fantasy_content"]["league"]["1"]
            if "teams" in league_data:
                for team in league_data["teams"].values():
                    if isinstance(team, dict) and "team" in team:
                        teams.append(team["team"])
        
        return teams
    
    async def get_team_roster(self, team_key: str, week: Optional[int] = None) -> Dict[str, Any]:
        """
        Get a team's roster for a specific week.
        
        Args:
            team_key: Yahoo team key
            week: Week number (optional, defaults to current week)
            
        Returns:
            Team roster information
        """
        endpoint = f"team/{team_key}/roster"
        params = {}
        
        if week:
            params["week"] = week
        
        response = await self._make_request(endpoint, params)
        
        if "fantasy_content" in response:
            return response["fantasy_content"]["team"]["1"]["roster"]
        
        raise ValueError("Invalid roster response format")
    
    async def get_league_players(self, league_key: str) -> List[Dict[str, Any]]:
        """
        Get all players in a league (rostered and free agents).
        
        Args:
            league_key: Yahoo league key
            
        Returns:
            List of players with their status and ownership
        """
        response = await self._make_request(f"league/{league_key}/players")
        
        players = []
        if "fantasy_content" in response:
            league_data = response["fantasy_content"]["league"]["1"]
            if "players" in league_data:
                for player in league_data["players"].values():
                    if isinstance(player, dict) and "player" in player:
                        players.append(player["player"])
        
        return players
    
    async def get_draft_results(self, league_key: str) -> List[Dict[str, Any]]:
        """
        Get draft results for a league.
        
        Args:
            league_key: Yahoo league key
            
        Returns:
            List of draft picks
        """
        response = await self._make_request(f"league/{league_key}/draftresults")
        
        picks = []
        if "fantasy_content" in response:
            league_data = response["fantasy_content"]["league"]["1"]
            if "draft_results" in league_data:
                for pick in league_data["draft_results"].values():
                    if isinstance(pick, dict) and "draft_result" in pick:
                        picks.append(pick["draft_result"])
        
        return picks
    
    async def get_league_transactions(self, league_key: str) -> List[Dict[str, Any]]:
        """
        Get recent transactions in a league.
        
        Args:
            league_key: Yahoo league key
            
        Returns:
            List of transactions
        """
        response = await self._make_request(f"league/{league_key}/transactions")
        
        transactions = []
        if "fantasy_content" in response:
            league_data = response["fantasy_content"]["league"]["1"]
            if "transactions" in league_data:
                for transaction in league_data["transactions"].values():
                    if isinstance(transaction, dict) and "transaction" in transaction:
                        transactions.append(transaction["transaction"])
        
        return transactions


class YahooAPIService:
    """Service for managing Yahoo API operations with token refresh."""
    
    def __init__(self, oauth_service: YahooOAuthService):
        self.oauth_service = oauth_service
        self._client: Optional[YahooAPIClient] = None
    
    async def get_client(self, access_token: str) -> YahooAPIClient:
        """
        Get a Yahoo API client with the provided access token.
        
        Args:
            access_token: Valid access token
            
        Returns:
            Yahoo API client
        """
        return YahooAPIClient(access_token)
    
    async def refresh_and_get_client(self, refresh_token: str) -> YahooAPIClient:
        """
        Refresh the access token and get a new API client.
        
        Args:
            refresh_token: Refresh token
            
        Returns:
            Yahoo API client with new access token
        """
        token_data = await self.oauth_service.refresh_token(refresh_token)
        parsed_tokens = self.oauth_service.parse_token_response(token_data)
        
        return YahooAPIClient(parsed_tokens["access_token"])
