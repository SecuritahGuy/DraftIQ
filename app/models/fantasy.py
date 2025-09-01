"""
Fantasy football database models for leagues, teams, players, and rosters.
"""

import json
from datetime import datetime
from typing import Any, Dict
from sqlalchemy import String, Integer, Boolean, Text, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class League(BaseModel):
    """Fantasy football league model."""
    
    __tablename__ = "leagues"
    
    # League identification
    league_key: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    season: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # League settings
    scoring_json: Mapped[str] = mapped_column(Text, nullable=True)  # JSON string of scoring rules
    roster_slots_json: Mapped[str] = mapped_column(Text, nullable=True)  # JSON string of roster slots
    
    # League metadata
    league_type: Mapped[str] = mapped_column(String, nullable=True)  # "public", "private"
    num_teams: Mapped[int] = mapped_column(Integer, nullable=True)
    is_finished: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Relationships
    teams = relationship("Team", back_populates="league", cascade="all, delete-orphan")
    league_players = relationship("LeaguePlayer", back_populates="league", cascade="all, delete-orphan")
    draft_picks = relationship("DraftPick", back_populates="league", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<League(league_key={self.league_key}, name={self.name}, season={self.season})>"
    
    @property
    def scoring_rules(self) -> Dict[str, Any]:
        """Get scoring rules as a dictionary."""
        if self.scoring_json:
            return json.loads(self.scoring_json)
        return {}
    
    @property
    def roster_slots(self) -> Dict[str, Any]:
        """Get roster slots as a dictionary."""
        if self.roster_slots_json:
            return json.loads(self.roster_slots_json)
        return {}


class Team(BaseModel):
    """Fantasy football team model."""
    
    __tablename__ = "teams"
    
    # Team identification
    team_key: Mapped[str] = mapped_column(String, primary_key=True)
    league_key: Mapped[str] = mapped_column(String, ForeignKey("leagues.league_key"), nullable=False)
    
    # Team information
    name: Mapped[str] = mapped_column(String, nullable=False)
    manager: Mapped[str] = mapped_column(String, nullable=True)
    
    # Team metadata
    division_id: Mapped[int] = mapped_column(Integer, nullable=True)
    rank: Mapped[int] = mapped_column(Integer, nullable=True)
    wins: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    losses: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    ties: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Relationships
    league = relationship("League", back_populates="teams")
    rosters = relationship("Roster", back_populates="team", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Team(team_key={self.team_key}, name={self.name}, league_key={self.league_key})>"


class Player(BaseModel):
    """NFL player model."""
    
    __tablename__ = "players"
    
    # Player identification
    player_id_yahoo: Mapped[str] = mapped_column(String, primary_key=True)
    gsis_id: Mapped[str] = mapped_column(String, nullable=True, index=True)
    pfr_id: Mapped[str] = mapped_column(String, nullable=True, index=True)
    
    # Player information
    full_name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    first_name: Mapped[str] = mapped_column(String, nullable=True)
    last_name: Mapped[str] = mapped_column(String, nullable=True)
    position: Mapped[str] = mapped_column(String, nullable=False, index=True)
    team: Mapped[str] = mapped_column(String, nullable=True, index=True)
    
    # Player metadata
    bye_week: Mapped[int] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Relationships
    league_players = relationship("LeaguePlayer", back_populates="player", cascade="all, delete-orphan")
    rosters = relationship("Roster", back_populates="player", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Player(player_id_yahoo={self.player_id_yahoo}, full_name={self.full_name}, position={self.position})>"


class LeaguePlayer(BaseModel):
    """Player status within a specific league."""
    
    __tablename__ = "league_players"
    
    # Composite primary key
    league_key: Mapped[str] = mapped_column(String, ForeignKey("leagues.league_key"), primary_key=True)
    player_id_yahoo: Mapped[str] = mapped_column(String, ForeignKey("players.player_id_yahoo"), primary_key=True)
    
    # Player status
    status: Mapped[str] = mapped_column(String, nullable=False, index=True)  # "FA", "WA", "IR", etc.
    percent_rostered: Mapped[float] = mapped_column(Integer, nullable=True)  # Percentage as integer (0-100)
    faab_cost_est: Mapped[int] = mapped_column(Integer, nullable=True)  # Estimated FAAB cost
    
    # Ownership information
    owner_team_key: Mapped[str] = mapped_column(String, ForeignKey("teams.team_key"), nullable=True)
    
    # Relationships
    league = relationship("League", back_populates="league_players")
    player = relationship("Player", back_populates="league_players")
    owner_team = relationship("Team")
    
    def __repr__(self) -> str:
        return f"<LeaguePlayer(league_key={self.league_key}, player_id_yahoo={self.player_id_yahoo}, status={self.status})>"


class Roster(BaseModel):
    """Team roster for a specific week."""
    
    __tablename__ = "rosters"
    
    # Roster identification
    team_key: Mapped[str] = mapped_column(String, ForeignKey("teams.team_key"), primary_key=True)
    week: Mapped[int] = mapped_column(Integer, primary_key=True)
    slot: Mapped[str] = mapped_column(String, primary_key=True)  # "QB", "RB", "WR", "TE", "FLEX", "BN", etc.
    
    # Player assignment
    player_id_yahoo: Mapped[str] = mapped_column(String, ForeignKey("players.player_id_yahoo"), nullable=True)
    
    # Roster metadata
    is_starting: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Relationships
    team = relationship("Team", back_populates="rosters")
    player = relationship("Player", back_populates="rosters")
    
    def __repr__(self) -> str:
        return f"<Roster(team_key={self.team_key}, week={self.week}, slot={self.slot}, player_id_yahoo={self.player_id_yahoo})>"


class DraftPick(BaseModel):
    """Draft pick information."""
    
    __tablename__ = "draft_picks"
    
    # Draft pick identification
    league_key: Mapped[str] = mapped_column(String, ForeignKey("leagues.league_key"), primary_key=True)
    round: Mapped[int] = mapped_column(Integer, primary_key=True)
    pick: Mapped[int] = mapped_column(Integer, primary_key=True)
    
    # Pick details
    team_key: Mapped[str] = mapped_column(String, ForeignKey("teams.team_key"), nullable=False)
    player_id_yahoo: Mapped[str] = mapped_column(String, ForeignKey("players.player_id_yahoo"), nullable=True)
    cost: Mapped[int] = mapped_column(Integer, nullable=True)  # For auction drafts
    
    # Relationships
    league = relationship("League", back_populates="draft_picks")
    team = relationship("Team")
    player = relationship("Player")
    
    def __repr__(self) -> str:
        return f"<DraftPick(league_key={self.league_key}, round={self.round}, pick={self.pick}, team_key={self.team_key})>"
