"""
NFL data models for statistics, projections, injuries, and depth charts.
"""

import json
from datetime import datetime
from typing import Any, Dict, Optional
from sqlalchemy import String, Integer, Boolean, Text, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import BaseModel


class WeeklyStats(BaseModel):
    """NFL player weekly statistics."""
    
    __tablename__ = "weekly_stats"
    
    # Player identification (using NFL's GSIS ID)
    gsis_id: Mapped[str] = mapped_column(String, primary_key=True)
    season: Mapped[int] = mapped_column(Integer, primary_key=True)
    week: Mapped[int] = mapped_column(Integer, primary_key=True)
    
    # Statistics stored as JSON for flexibility
    stat_json: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Metadata
    team: Mapped[str] = mapped_column(String, nullable=False, index=True)
    opponent: Mapped[str] = mapped_column(String, nullable=True)
    game_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self) -> str:
        return f"<WeeklyStats(gsis_id={self.gsis_id}, season={self.season}, week={self.week})>"
    
    @property
    def stats(self) -> Dict[str, Any]:
        """Get statistics as a dictionary."""
        return json.loads(self.stat_json)
    
    @property
    def fantasy_points(self) -> float:
        """Calculate fantasy points from stats (basic calculation)."""
        stats = self.stats
        # This is a placeholder - actual calculation will be done by scoring engine
        return 0.0


class WeeklyProjections(BaseModel):
    """Fantasy football weekly projections."""
    
    __tablename__ = "weekly_projections"
    
    # Player identification
    gsis_id: Mapped[str] = mapped_column(String, primary_key=True)
    season: Mapped[int] = mapped_column(Integer, primary_key=True)
    week: Mapped[int] = mapped_column(Integer, primary_key=True)
    source: Mapped[str] = mapped_column(String, primary_key=True)  # "internal", "csv", "external"
    
    # Projection data
    proj_json: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # 0.0-1.0 confidence score
    
    def __repr__(self) -> str:
        return f"<WeeklyProjections(gsis_id={self.gsis_id}, season={self.season}, week={self.week}, source={self.source})>"
    
    @property
    def projections(self) -> Dict[str, Any]:
        """Get projections as a dictionary."""
        return json.loads(self.proj_json)


class Injuries(BaseModel):
    """Player injury information."""
    
    __tablename__ = "injuries"
    
    # Player identification
    gsis_id: Mapped[str] = mapped_column(String, primary_key=True)
    week: Mapped[int] = mapped_column(Integer, primary_key=True)
    season: Mapped[int] = mapped_column(Integer, primary_key=True)
    
    # Injury information
    status: Mapped[str] = mapped_column(String, nullable=False, index=True)  # "Questionable", "Doubtful", "Out", "IR"
    report: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Injury report details
    practice_status: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # "Full", "Limited", "DNP"
    
    # Metadata
    team: Mapped[str] = mapped_column(String, nullable=False, index=True)
    position: Mapped[str] = mapped_column(String, nullable=False, index=True)
    
    def __repr__(self) -> str:
        return f"<Injuries(gsis_id={self.gsis_id}, week={self.week}, status={self.status})>"
    
    @property
    def is_out(self) -> bool:
        """Check if player is out for the week."""
        return self.status in ["Out", "IR", "PUP"]
    
    @property
    def is_questionable(self) -> bool:
        """Check if player is questionable."""
        return self.status in ["Questionable", "Doubtful"]


class DepthCharts(BaseModel):
    """Team depth chart information."""
    
    __tablename__ = "depth_charts"
    
    # Depth chart identification
    team: Mapped[str] = mapped_column(String, primary_key=True)
    week: Mapped[int] = mapped_column(Integer, primary_key=True)
    season: Mapped[int] = mapped_column(Integer, primary_key=True)
    position: Mapped[str] = mapped_column(String, primary_key=True)
    
    # Player information
    gsis_id: Mapped[str] = mapped_column(String, nullable=False)
    depth_order: Mapped[int] = mapped_column(Integer, nullable=False)  # 1 = starter, 2 = backup, etc.
    
    # Metadata
    role: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # "Starter", "Backup", "Practice Squad"
    
    def __repr__(self) -> str:
        return f"<DepthCharts(team={self.team}, week={self.week}, position={self.position}, depth_order={self.depth_order})>"
    
    @property
    def is_starter(self) -> bool:
        """Check if player is a starter."""
        return self.depth_order == 1


class PlayerIDMapping(BaseModel):
    """Player ID mapping between different data sources."""
    
    __tablename__ = "player_id_mapping"
    
    # Primary identifiers
    gsis_id: Mapped[str] = mapped_column(String, primary_key=True)
    pfr_id: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True)
    espn_id: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True)
    
    # Player information
    full_name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    first_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    position: Mapped[str] = mapped_column(String, nullable=False, index=True)
    team: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True)
    
    # Mapping metadata
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Mapping confidence score
    
    def __repr__(self) -> str:
        return f"<PlayerIDMapping(gsis_id={self.gsis_id}, full_name={self.full_name}, position={self.position})>"


class Recommendations(BaseModel):
    """Start/sit recommendations for teams."""
    
    __tablename__ = "recommendations"
    
    # Recommendation identification
    team_key: Mapped[str] = mapped_column(String, primary_key=True)
    week: Mapped[int] = mapped_column(Integer, primary_key=True)
    season: Mapped[int] = mapped_column(Integer, primary_key=True)
    
    # Recommendation data
    lineup_json: Mapped[str] = mapped_column(Text, nullable=False)  # Optimal lineup
    delta_points: Mapped[float] = mapped_column(Float, nullable=False)  # Points gained vs current lineup
    
    # Metadata
    algorithm_version: Mapped[str] = mapped_column(String, nullable=False)  # Version of recommendation algorithm
    confidence: Mapped[float] = mapped_column(Float, nullable=False)  # Confidence in recommendation (0.0-1.0)
    reasoning: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Explanation for recommendation
    
    def __repr__(self) -> str:
        return f"<Recommendations(team_key={self.team_key}, week={self.week}, delta_points={self.delta_points})>"
    
    @property
    def lineup(self) -> Dict[str, Any]:
        """Get lineup as a dictionary."""
        return json.loads(self.lineup_json)
