"""
Pydantic schemas for Yahoo API sync endpoints and responses.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class LeagueInfo(BaseModel):
    """League information from Yahoo API."""
    
    league_key: str = Field(..., description="Yahoo league key")
    name: str = Field(..., description="League name")
    season: int = Field(..., description="Season year")
    league_type: Optional[str] = Field(default=None, description="League type (public/private)")
    num_teams: Optional[int] = Field(default=None, description="Number of teams")
    is_finished: bool = Field(default=False, description="Whether league is finished")
    
    class Config:
        json_schema_extra = {
            "example": {
                "league_key": "414.l.123456",
                "name": "My Fantasy League",
                "season": 2024,
                "league_type": "private",
                "num_teams": 12,
                "is_finished": False
            }
        }


class TeamInfo(BaseModel):
    """Team information from Yahoo API."""
    
    team_key: str = Field(..., description="Yahoo team key")
    name: str = Field(..., description="Team name")
    manager: Optional[str] = Field(default=None, description="Team manager name")
    division_id: Optional[int] = Field(default=None, description="Division ID")
    rank: Optional[int] = Field(default=None, description="Current rank")
    wins: int = Field(default=0, description="Number of wins")
    losses: int = Field(default=0, description="Number of losses")
    ties: int = Field(default=0, description="Number of ties")
    
    class Config:
        json_schema_extra = {
            "example": {
                "team_key": "414.l.123456.t.1",
                "name": "Team Awesome",
                "manager": "John Doe",
                "division_id": 1,
                "rank": 3,
                "wins": 8,
                "losses": 4,
                "ties": 0
            }
        }


class PlayerInfo(BaseModel):
    """Player information from Yahoo API."""
    
    player_id_yahoo: str = Field(..., description="Yahoo player ID")
    full_name: str = Field(..., description="Player full name")
    first_name: Optional[str] = Field(default=None, description="Player first name")
    last_name: Optional[str] = Field(default=None, description="Player last name")
    position: str = Field(..., description="Player position")
    team: Optional[str] = Field(default=None, description="NFL team")
    bye_week: Optional[int] = Field(default=None, description="Bye week")
    is_active: bool = Field(default=True, description="Whether player is active")
    
    class Config:
        json_schema_extra = {
            "example": {
                "player_id_yahoo": "12345",
                "full_name": "Patrick Mahomes",
                "first_name": "Patrick",
                "last_name": "Mahomes",
                "position": "QB",
                "team": "KC",
                "bye_week": 10,
                "is_active": True
            }
        }


class RosterSlot(BaseModel):
    """Roster slot information."""
    
    slot: str = Field(..., description="Roster slot (QB, RB, WR, TE, FLEX, BN, etc.)")
    player_id_yahoo: Optional[str] = Field(default=None, description="Yahoo player ID")
    is_starting: bool = Field(default=False, description="Whether player is in starting lineup")
    
    class Config:
        json_schema_extra = {
            "example": {
                "slot": "QB",
                "player_id_yahoo": "12345",
                "is_starting": True
            }
        }


class TeamRoster(BaseModel):
    """Team roster for a specific week."""
    
    team_key: str = Field(..., description="Yahoo team key")
    week: int = Field(..., description="Week number")
    slots: List[RosterSlot] = Field(..., description="Roster slots")
    
    class Config:
        json_schema_extra = {
            "example": {
                "team_key": "414.l.123456.t.1",
                "week": 1,
                "slots": [
                    {"slot": "QB", "player_id_yahoo": "12345", "is_starting": True},
                    {"slot": "RB", "player_id_yahoo": "67890", "is_starting": True},
                    {"slot": "BN", "player_id_yahoo": "11111", "is_starting": False}
                ]
            }
        }


class LeaguePlayerStatus(BaseModel):
    """Player status within a league."""
    
    player_id_yahoo: str = Field(..., description="Yahoo player ID")
    status: str = Field(..., description="Player status (FA, WA, IR, etc.)")
    percent_rostered: Optional[int] = Field(default=None, description="Percentage rostered (0-100)")
    faab_cost_est: Optional[int] = Field(default=None, description="Estimated FAAB cost")
    owner_team_key: Optional[str] = Field(default=None, description="Owner team key if rostered")
    
    class Config:
        json_schema_extra = {
            "example": {
                "player_id_yahoo": "12345",
                "status": "FA",
                "percent_rostered": 85,
                "faab_cost_est": 15,
                "owner_team_key": None
            }
        }


class DraftPickInfo(BaseModel):
    """Draft pick information."""
    
    round: int = Field(..., description="Draft round")
    pick: int = Field(..., description="Pick number in round")
    team_key: str = Field(..., description="Team that made the pick")
    player_id_yahoo: Optional[str] = Field(default=None, description="Player drafted")
    cost: Optional[int] = Field(default=None, description="Auction cost if applicable")
    
    class Config:
        json_schema_extra = {
            "example": {
                "round": 1,
                "pick": 1,
                "team_key": "414.l.123456.t.1",
                "player_id_yahoo": "12345",
                "cost": None
            }
        }


class LeagueSyncRequest(BaseModel):
    """Request to sync league data."""
    
    include_teams: bool = Field(default=True, description="Include team data")
    include_players: bool = Field(default=True, description="Include player data")
    include_draft: bool = Field(default=True, description="Include draft results")
    include_transactions: bool = Field(default=False, description="Include recent transactions")


class LeagueSyncResponse(BaseModel):
    """Response from league sync operation."""
    
    success: bool = Field(..., description="Whether sync was successful")
    league_key: str = Field(..., description="League key that was synced")
    message: str = Field(..., description="Sync result message")
    teams_synced: Optional[int] = Field(default=None, description="Number of teams synced")
    players_synced: Optional[int] = Field(default=None, description="Number of players synced")
    draft_picks_synced: Optional[int] = Field(default=None, description="Number of draft picks synced")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "league_key": "414.l.123456",
                "message": "League synced successfully",
                "teams_synced": 12,
                "players_synced": 180,
                "draft_picks_synced": 144
            }
        }


class UserLeaguesResponse(BaseModel):
    """Response for user leagues endpoint."""
    
    leagues: List[LeagueInfo] = Field(..., description="User's leagues")
    total_count: int = Field(..., description="Total number of leagues")
    
    class Config:
        json_schema_extra = {
            "example": {
                "leagues": [
                    {
                        "league_key": "414.l.123456",
                        "name": "My Fantasy League",
                        "season": 2024,
                        "league_type": "private",
                        "num_teams": 12,
                        "is_finished": False
                    }
                ],
                "total_count": 1
            }
        }


class SyncError(BaseModel):
    """Error response for sync operations."""
    
    error: str = Field(..., description="Error type")
    error_description: str = Field(..., description="Error description")
    league_key: Optional[str] = Field(default=None, description="League key if applicable")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "league_not_found",
                "error_description": "League with key 414.l.123456 not found",
                "league_key": "414.l.123456"
            }
        }
