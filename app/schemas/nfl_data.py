"""
Pydantic schemas for NFL data models and API responses.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class WeeklyStatsResponse(BaseModel):
    """Response schema for weekly statistics."""
    
    gsis_id: str = Field(..., description="Player GSIS ID")
    season: int = Field(..., description="NFL season year")
    week: int = Field(..., description="Week number")
    team: str = Field(..., description="Player's team")
    opponent: Optional[str] = Field(None, description="Opponent team")
    game_date: Optional[datetime] = Field(None, description="Game date")
    stats: Dict[str, Any] = Field(..., description="Player statistics")
    fantasy_points: float = Field(..., description="Calculated fantasy points")


class InjuryResponse(BaseModel):
    """Response schema for injury information."""
    
    gsis_id: str = Field(..., description="Player GSIS ID")
    season: int = Field(..., description="NFL season year")
    week: int = Field(..., description="Week number")
    status: str = Field(..., description="Injury status")
    report: Optional[str] = Field(None, description="Injury report details")
    practice_status: Optional[str] = Field(None, description="Practice status")
    team: str = Field(..., description="Player's team")
    position: str = Field(..., description="Player position")
    is_out: bool = Field(..., description="Whether player is out")
    is_questionable: bool = Field(..., description="Whether player is questionable")


class DepthChartEntry(BaseModel):
    """Schema for depth chart entry."""
    
    gsis_id: str = Field(..., description="Player GSIS ID")
    depth_order: int = Field(..., description="Depth order (1 = starter)")
    role: Optional[str] = Field(None, description="Player role")
    is_starter: bool = Field(..., description="Whether player is starter")


class DepthChartResponse(BaseModel):
    """Response schema for team depth chart."""
    
    team: str = Field(..., description="Team abbreviation")
    season: int = Field(..., description="NFL season year")
    week: int = Field(..., description="Week number")
    depth_chart: Dict[str, List[DepthChartEntry]] = Field(..., description="Depth chart by position")


class NFLDataImportResponse(BaseModel):
    """Response schema for NFL data import operations."""
    
    success: bool = Field(..., description="Whether import was successful")
    message: str = Field(..., description="Import result message")
    
    # Weekly stats fields
    stats_created: Optional[int] = Field(None, description="Number of stats records created")
    stats_updated: Optional[int] = Field(None, description="Number of stats records updated")
    total_processed: Optional[int] = Field(None, description="Total records processed")
    
    # Injury fields
    injuries_created: Optional[int] = Field(None, description="Number of injury records created")
    injuries_updated: Optional[int] = Field(None, description="Number of injury records updated")
    
    # Depth chart fields
    charts_created: Optional[int] = Field(None, description="Number of depth chart records created")
    charts_updated: Optional[int] = Field(None, description="Number of depth chart records updated")
    
    # Error fields
    failed_imports: Optional[List[str]] = Field(None, description="List of failed imports")
    error: Optional[str] = Field(None, description="Error message")


class AllNFLDataImportResponse(BaseModel):
    """Response schema for importing all NFL data types."""
    
    success: bool = Field(..., description="Whether all imports were successful")
    message: str = Field(..., description="Import result message")
    
    # Individual import results
    weekly_stats: Dict[str, Any] = Field(..., description="Weekly stats import result")
    injuries: Dict[str, Any] = Field(..., description="Injuries import result")
    depth_charts: Dict[str, Any] = Field(..., description="Depth charts import result")
    snap_counts: Dict[str, Any] = Field(..., description="Snap counts import result")
    
    # Error fields
    failed_imports: Optional[List[str]] = Field(None, description="List of failed imports")


class ProjectionRequest(BaseModel):
    """Request schema for creating projections."""
    
    gsis_id: str = Field(..., description="Player GSIS ID")
    season: int = Field(..., description="NFL season year")
    week: int = Field(..., description="Week number")
    source: str = Field(default="internal", description="Projection source")
    projections: Dict[str, Any] = Field(..., description="Projection data")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence score")


class ProjectionResponse(BaseModel):
    """Response schema for projections."""
    
    gsis_id: str = Field(..., description="Player GSIS ID")
    season: int = Field(..., description="NFL season year")
    week: int = Field(..., description="Week number")
    source: str = Field(..., description="Projection source")
    projections: Dict[str, Any] = Field(..., description="Projection data")
    confidence: Optional[float] = Field(None, description="Confidence score")
    created_at: datetime = Field(..., description="Creation timestamp")


class ScoringRule(BaseModel):
    """Schema for individual scoring rules."""
    
    stat: str = Field(..., description="Statistic name")
    points: float = Field(..., description="Points per unit")
    threshold: Optional[float] = Field(None, description="Minimum threshold for points")
    max_points: Optional[float] = Field(None, description="Maximum points for this stat")


class ScoringSystem(BaseModel):
    """Schema for complete scoring system."""
    
    passing_yards: Optional[ScoringRule] = Field(None, description="Passing yards scoring")
    passing_tds: Optional[ScoringRule] = Field(None, description="Passing TDs scoring")
    passing_ints: Optional[ScoringRule] = Field(None, description="Passing interceptions scoring")
    rushing_yards: Optional[ScoringRule] = Field(None, description="Rushing yards scoring")
    rushing_tds: Optional[ScoringRule] = Field(None, description="Rushing TDs scoring")
    receiving_yards: Optional[ScoringRule] = Field(None, description="Receiving yards scoring")
    receiving_tds: Optional[ScoringRule] = Field(None, description="Receiving TDs scoring")
    receptions: Optional[ScoringRule] = Field(None, description="Receptions scoring")
    fumbles_lost: Optional[ScoringRule] = Field(None, description="Fumbles lost scoring")
    field_goals: Optional[ScoringRule] = Field(None, description="Field goals scoring")
    extra_points: Optional[ScoringRule] = Field(None, description="Extra points scoring")


class FantasyPointsResponse(BaseModel):
    """Response schema for calculated fantasy points."""
    
    gsis_id: str = Field(..., description="Player GSIS ID")
    season: int = Field(..., description="NFL season year")
    week: int = Field(..., description="Week number")
    fantasy_points: float = Field(..., description="Calculated fantasy points")
    scoring_breakdown: Dict[str, float] = Field(..., description="Points breakdown by stat")
    scoring_system: ScoringSystem = Field(..., description="Scoring system used")
