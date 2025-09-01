"""
Data synchronization service for persisting Yahoo API data and managing caching.
"""

import json
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from app.models.fantasy import League, Team, Player, LeaguePlayer, Roster, DraftPick
from app.models.nfl_data import WeeklyStats, WeeklyProjections, Injuries, DepthCharts, PlayerIDMapping
from app.services.yahoo_api import YahooAPIClient


class DataSyncService:
    """Service for synchronizing data between Yahoo API and local database."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def sync_league_data(self, league_data: Dict[str, Any]) -> League:
        """
        Sync league data from Yahoo API.
        
        Args:
            league_data: League data from Yahoo API
            
        Returns:
            Updated League model
        """
        league_key = league_data.get("league_key")
        if not league_key:
            raise ValueError("League key is required")
        
        # Check if league exists
        stmt = select(League).where(League.league_key == league_key)
        result = await self.db.execute(stmt)
        existing_league = result.scalar_one_or_none()
        
        # Prepare league data
        league_dict = {
            "league_key": league_key,
            "name": league_data.get("name", ""),
            "season": league_data.get("season", datetime.now().year),
            "league_type": league_data.get("league_type"),
            "num_teams": league_data.get("num_teams"),
            "is_finished": league_data.get("is_finished", False)
        }
        
        # Handle scoring rules
        if "settings" in league_data and "scoring_settings" in league_data["settings"]:
            league_dict["scoring_json"] = json.dumps(league_data["settings"]["scoring_settings"])
        
        # Handle roster slots
        if "settings" in league_data and "roster_positions" in league_data["settings"]:
            league_dict["roster_slots_json"] = json.dumps(league_data["settings"]["roster_positions"])
        
        if existing_league:
            # Update existing league
            for key, value in league_dict.items():
                setattr(existing_league, key, value)
            league = existing_league
        else:
            # Create new league
            league = League(**league_dict)
            self.db.add(league)
        
        await self.db.commit()
        await self.db.refresh(league)
        return league
    
    async def sync_teams_data(self, league_key: str, teams_data: List[Dict[str, Any]]) -> List[Team]:
        """
        Sync teams data for a league.
        
        Args:
            league_key: League key
            teams_data: List of team data from Yahoo API
            
        Returns:
            List of updated Team models
        """
        teams = []
        
        for team_data in teams_data:
            team_key = team_data.get("team_key")
            if not team_key:
                continue
            
            # Check if team exists
            stmt = select(Team).where(Team.team_key == team_key)
            result = await self.db.execute(stmt)
            existing_team = result.scalar_one_or_none()
            
            # Prepare team data
            team_dict = {
                "team_key": team_key,
                "league_key": league_key,
                "name": team_data.get("name", ""),
                "manager": team_data.get("managers", [{}])[0].get("nickname") if team_data.get("managers") else None,
                "division_id": team_data.get("division_id"),
                "rank": team_data.get("team_standings", {}).get("rank"),
                "wins": team_data.get("team_standings", {}).get("outcome_totals", {}).get("wins", 0),
                "losses": team_data.get("team_standings", {}).get("outcome_totals", {}).get("losses", 0),
                "ties": team_data.get("team_standings", {}).get("outcome_totals", {}).get("ties", 0)
            }
            
            if existing_team:
                # Update existing team
                for key, value in team_dict.items():
                    setattr(existing_team, key, value)
                team = existing_team
            else:
                # Create new team
                team = Team(**team_dict)
                self.db.add(team)
            
            teams.append(team)
        
        await self.db.commit()
        for team in teams:
            await self.db.refresh(team)
        
        return teams
    
    async def sync_players_data(self, league_key: str, players_data: List[Dict[str, Any]]) -> List[Player]:
        """
        Sync players data for a league.
        
        Args:
            league_key: League key
            players_data: List of player data from Yahoo API
            
        Returns:
            List of updated Player models
        """
        players = []
        
        for player_data in players_data:
            player_id_yahoo = player_data.get("player_id")
            if not player_id_yahoo:
                continue
            
            # Check if player exists
            stmt = select(Player).where(Player.player_id_yahoo == player_id_yahoo)
            result = await self.db.execute(stmt)
            existing_player = result.scalar_one_or_none()
            
            # Prepare player data
            player_dict = {
                "player_id_yahoo": player_id_yahoo,
                "full_name": player_data.get("name", {}).get("full", ""),
                "first_name": player_data.get("name", {}).get("first", ""),
                "last_name": player_data.get("name", {}).get("last", ""),
                "position": player_data.get("display_position", ""),
                "team": player_data.get("editorial_team_abbr"),
                "bye_week": player_data.get("bye_weeks", {}).get("week"),
                "is_active": True
            }
            
            if existing_player:
                # Update existing player
                for key, value in player_dict.items():
                    setattr(existing_player, key, value)
                player = existing_player
            else:
                # Create new player
                player = Player(**player_dict)
                self.db.add(player)
            
            players.append(player)
        
        await self.db.commit()
        for player in players:
            await self.db.refresh(player)
        
        return players
    
    async def sync_league_players_data(self, league_key: str, players_data: List[Dict[str, Any]]) -> List[LeaguePlayer]:
        """
        Sync league-specific player data (ownership, status, etc.).
        
        Args:
            league_key: League key
            players_data: List of player data from Yahoo API
            
        Returns:
            List of updated LeaguePlayer models
        """
        league_players = []
        
        for player_data in players_data:
            player_id_yahoo = player_data.get("player_id")
            if not player_id_yahoo:
                continue
            
            # Check if league player exists
            stmt = select(LeaguePlayer).where(
                LeaguePlayer.league_key == league_key,
                LeaguePlayer.player_id_yahoo == player_id_yahoo
            )
            result = await self.db.execute(stmt)
            existing_league_player = result.scalar_one_or_none()
            
            # Prepare league player data
            league_player_dict = {
                "league_key": league_key,
                "player_id_yahoo": player_id_yahoo,
                "status": player_data.get("status", "FA"),
                "percent_rostered": player_data.get("percent_owned"),
                "owner_team_key": player_data.get("selected_position", {}).get("team_key")
            }
            
            if existing_league_player:
                # Update existing league player
                for key, value in league_player_dict.items():
                    setattr(existing_league_player, key, value)
                league_player = existing_league_player
            else:
                # Create new league player
                league_player = LeaguePlayer(**league_player_dict)
                self.db.add(league_player)
            
            league_players.append(league_player)
        
        await self.db.commit()
        for league_player in league_players:
            await self.db.refresh(league_player)
        
        return league_players
    
    async def sync_roster_data(self, team_key: str, week: int, roster_data: Dict[str, Any]) -> List[Roster]:
        """
        Sync roster data for a team.
        
        Args:
            team_key: Team key
            week: Week number
            roster_data: Roster data from Yahoo API
            
        Returns:
            List of updated Roster models
        """
        rosters = []
        
        # Clear existing roster for this team/week
        stmt = select(Roster).where(Roster.team_key == team_key, Roster.week == week)
        result = await self.db.execute(stmt)
        existing_rosters = result.scalars().all()
        
        for existing_roster in existing_rosters:
            await self.db.delete(existing_roster)
        
        # Add new roster entries
        if "0" in roster_data and "players" in roster_data["0"]:
            for player_data in roster_data["0"]["players"].values():
                if isinstance(player_data, dict) and "player" in player_data:
                    player = player_data["player"]
                    
                    roster_dict = {
                        "team_key": team_key,
                        "week": week,
                        "slot": player_data.get("selected_position", {}).get("position", "BN"),
                        "player_id_yahoo": player.get("player_id"),
                        "is_starting": player_data.get("selected_position", {}).get("position") != "BN"
                    }
                    
                    roster = Roster(**roster_dict)
                    self.db.add(roster)
                    rosters.append(roster)
        
        await self.db.commit()
        for roster in rosters:
            await self.db.refresh(roster)
        
        return rosters
    
    async def sync_draft_data(self, league_key: str, draft_data: List[Dict[str, Any]]) -> List[DraftPick]:
        """
        Sync draft data for a league.
        
        Args:
            league_key: League key
            draft_data: List of draft pick data from Yahoo API
            
        Returns:
            List of updated DraftPick models
        """
        draft_picks = []
        
        # Clear existing draft picks for this league
        stmt = select(DraftPick).where(DraftPick.league_key == league_key)
        result = await self.db.execute(stmt)
        existing_picks = result.scalars().all()
        
        for existing_pick in existing_picks:
            await self.db.delete(existing_pick)
        
        # Add new draft picks
        for pick_data in draft_data:
            draft_pick_dict = {
                "league_key": league_key,
                "round": pick_data.get("round", 0),
                "pick": pick_data.get("pick", 0),
                "team_key": pick_data.get("team_key"),
                "player_id_yahoo": pick_data.get("player_id"),
                "cost": pick_data.get("cost")  # For auction drafts
            }
            
            draft_pick = DraftPick(**draft_pick_dict)
            self.db.add(draft_pick)
            draft_picks.append(draft_pick)
        
        await self.db.commit()
        for draft_pick in draft_picks:
            await self.db.refresh(draft_pick)
        
        return draft_picks
    
    async def get_cached_league_data(self, league_key: str, max_age_hours: int = 24) -> Optional[Dict[str, Any]]:
        """
        Get cached league data if it's recent enough.
        
        Args:
            league_key: League key
            max_age_hours: Maximum age of cached data in hours
            
        Returns:
            Cached league data or None if too old
        """
        stmt = select(League).where(League.league_key == league_key)
        result = await self.db.execute(stmt)
        league = result.scalar_one_or_none()
        
        if not league:
            return None
        
        # Check if data is recent enough
        max_age = timedelta(hours=max_age_hours)
        if datetime.now(timezone.utc) - league.updated_at > max_age:
            return None
        
        # Return cached data
        return {
            "league": league,
            "teams": await self.get_league_teams(league_key),
            "players": await self.get_league_players(league_key)
        }
    
    async def get_league_teams(self, league_key: str) -> List[Team]:
        """Get all teams for a league."""
        stmt = select(Team).where(Team.league_key == league_key)
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def get_league_players(self, league_key: str) -> List[LeaguePlayer]:
        """Get all players for a league."""
        stmt = select(LeaguePlayer).where(LeaguePlayer.league_key == league_key)
        result = await self.db.execute(stmt)
        return result.scalars().all()
