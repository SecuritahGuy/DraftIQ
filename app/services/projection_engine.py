"""
Fantasy football projection engine using usage-driven models.
"""

import json
import math
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

from app.models.nfl_data import WeeklyStats, WeeklyProjections, Injuries, DepthCharts, PlayerIDMapping
from app.models.fantasy import Player


@dataclass
class ProjectionInputs:
    """Input data for generating projections."""
    recent_stats: List[Dict[str, Any]]
    depth_chart_order: int
    snap_share: float
    injury_status: Optional[str]
    opponent_defense: Dict[str, float]
    team_offense: Dict[str, float]
    weather_conditions: Optional[Dict[str, Any]] = None


@dataclass
class ProjectionOutput:
    """Output projection data."""
    passing_yards: float = 0.0
    passing_tds: float = 0.0
    passing_ints: float = 0.0
    rushing_yards: float = 0.0
    rushing_tds: float = 0.0
    receiving_yards: float = 0.0
    receiving_tds: float = 0.0
    receptions: float = 0.0
    fumbles_lost: float = 0.0
    field_goals: float = 0.0
    field_goal_attempts: float = 0.0
    extra_points: float = 0.0
    extra_point_attempts: float = 0.0
    confidence: float = 0.5


class UsageDrivenProjectionModel:
    """Base class for usage-driven projection models."""
    
    def __init__(self, position: str):
        self.position = position
    
    def calculate_usage_factor(self, depth_order: int, snap_share: float) -> float:
        """Calculate usage factor based on depth chart and snap share."""
        # Depth chart factor (starter = 1.0, backup = 0.5, etc.)
        depth_factor = max(0.1, 1.0 / depth_order)
        
        # Snap share factor (normalize to 0-1 range)
        snap_factor = min(1.0, snap_share / 100.0)
        
        # Combine factors with weights
        return (depth_factor * 0.6) + (snap_factor * 0.4)
    
    def apply_injury_adjustment(self, base_projection: ProjectionOutput, injury_status: Optional[str]) -> ProjectionOutput:
        """Apply injury-based adjustments to projections."""
        if not injury_status:
            return base_projection
        
        injury_adjustments = {
            "Out": 0.0,
            "IR": 0.0,
            "PUP": 0.0,
            "Doubtful": 0.1,
            "Questionable": 0.3,
            "Probable": 0.7,
            "Full": 1.0
        }
        
        adjustment_factor = injury_adjustments.get(injury_status, 0.5)
        
        # Apply adjustment to all stats
        for field in base_projection.__dataclass_fields__:
            if field != 'confidence':
                current_value = getattr(base_projection, field)
                setattr(base_projection, field, current_value * adjustment_factor)
        
        # Reduce confidence for injured players
        base_projection.confidence *= adjustment_factor
        
        return base_projection


class QBProjectionModel(UsageDrivenProjectionModel):
    """Quarterback projection model."""
    
    def __init__(self):
        super().__init__("QB")
    
    def generate_projection(self, inputs: ProjectionInputs) -> ProjectionOutput:
        """Generate QB projections."""
        usage_factor = self.calculate_usage_factor(inputs.depth_chart_order, inputs.snap_share)
        
        # Base projections from recent performance
        base_proj = self._calculate_base_projections(inputs.recent_stats)
        
        # Apply usage factor
        base_proj.passing_yards *= usage_factor
        base_proj.passing_tds *= usage_factor
        base_proj.passing_ints *= usage_factor
        base_proj.rushing_yards *= usage_factor * 0.3  # QBs rush less
        base_proj.rushing_tds *= usage_factor * 0.2
        
        # Apply opponent defense adjustments
        base_proj = self._apply_defense_adjustments(base_proj, inputs.opponent_defense)
        
        # Apply injury adjustments
        base_proj = self.apply_injury_adjustment(base_proj, inputs.injury_status)
        
        return base_proj
    
    def _calculate_base_projections(self, recent_stats: List[Dict[str, Any]]) -> ProjectionOutput:
        """Calculate base projections from recent stats."""
        if not recent_stats:
            return ProjectionOutput()
        
        # Use last 4 games for QB projections
        recent_games = recent_stats[-4:] if len(recent_stats) >= 4 else recent_stats
        
        # Calculate averages with recent game weighting
        weights = [0.4, 0.3, 0.2, 0.1][:len(recent_games)]
        total_weight = sum(weights)
        
        proj = ProjectionOutput()
        
        for i, game in enumerate(recent_games):
            weight = weights[i] / total_weight
            proj.passing_yards += game.get('passing_yards', 0) * weight
            proj.passing_tds += game.get('passing_tds', 0) * weight
            proj.passing_ints += game.get('passing_ints', 0) * weight
            proj.rushing_yards += game.get('rushing_yards', 0) * weight
            proj.rushing_tds += game.get('rushing_tds', 0) * weight
        
        # Add some regression to mean
        proj.passing_yards *= 0.9  # Slight regression
        proj.passing_tds *= 0.95
        proj.passing_ints *= 1.05  # Slight increase for variance
        
        return proj
    
    def _apply_defense_adjustments(self, proj: ProjectionOutput, defense: Dict[str, float]) -> ProjectionOutput:
        """Apply opponent defense adjustments."""
        # Defense rankings (lower is better for offense)
        pass_def_rank = defense.get('pass_defense_rank', 16)  # Average
        rush_def_rank = defense.get('rush_defense_rank', 16)
        
        # Convert rank to multiplier (rank 1 = 1.2x, rank 32 = 0.8x)
        pass_multiplier = 1.2 - (pass_def_rank - 1) * 0.0125
        rush_multiplier = 1.2 - (rush_def_rank - 1) * 0.0125
        
        proj.passing_yards *= pass_multiplier
        proj.passing_tds *= pass_multiplier
        proj.rushing_yards *= rush_multiplier
        proj.rushing_tds *= rush_multiplier
        
        return proj


class RBProjectionModel(UsageDrivenProjectionModel):
    """Running back projection model."""
    
    def __init__(self):
        super().__init__("RB")
    
    def generate_projection(self, inputs: ProjectionInputs) -> ProjectionOutput:
        """Generate RB projections."""
        usage_factor = self.calculate_usage_factor(inputs.depth_chart_order, inputs.snap_share)
        
        # Base projections from recent performance
        base_proj = self._calculate_base_projections(inputs.recent_stats)
        
        # Apply usage factor (RBs are more usage-dependent)
        base_proj.rushing_yards *= usage_factor
        base_proj.rushing_tds *= usage_factor
        base_proj.receiving_yards *= usage_factor * 0.8  # Receiving less usage-dependent
        base_proj.receiving_tds *= usage_factor * 0.8
        base_proj.receptions *= usage_factor * 0.8
        
        # Apply opponent defense adjustments
        base_proj = self._apply_defense_adjustments(base_proj, inputs.opponent_defense)
        
        # Apply injury adjustments
        base_proj = self.apply_injury_adjustment(base_proj, inputs.injury_status)
        
        return base_proj
    
    def _calculate_base_projections(self, recent_stats: List[Dict[str, Any]]) -> ProjectionOutput:
        """Calculate base projections from recent stats."""
        if not recent_stats:
            return ProjectionOutput()
        
        # Use last 3 games for RB projections (more volatile)
        recent_games = recent_stats[-3:] if len(recent_stats) >= 3 else recent_stats
        
        # Calculate averages with recent game weighting
        weights = [0.5, 0.3, 0.2][:len(recent_games)]
        total_weight = sum(weights)
        
        proj = ProjectionOutput()
        
        for i, game in enumerate(recent_games):
            weight = weights[i] / total_weight
            proj.rushing_yards += game.get('rushing_yards', 0) * weight
            proj.rushing_tds += game.get('rushing_tds', 0) * weight
            proj.receiving_yards += game.get('receiving_yards', 0) * weight
            proj.receiving_tds += game.get('receiving_tds', 0) * weight
            proj.receptions += game.get('receptions', 0) * weight
        
        # Add regression to mean
        proj.rushing_yards *= 0.85
        proj.rushing_tds *= 0.9
        proj.receiving_yards *= 0.9
        proj.receiving_tds *= 0.9
        proj.receptions *= 0.9
        
        return proj
    
    def _apply_defense_adjustments(self, proj: ProjectionOutput, defense: Dict[str, float]) -> ProjectionOutput:
        """Apply opponent defense adjustments."""
        rush_def_rank = defense.get('rush_defense_rank', 16)
        pass_def_rank = defense.get('pass_defense_rank', 16)
        
        rush_multiplier = 1.2 - (rush_def_rank - 1) * 0.0125
        pass_multiplier = 1.2 - (pass_def_rank - 1) * 0.0125
        
        proj.rushing_yards *= rush_multiplier
        proj.rushing_tds *= rush_multiplier
        proj.receiving_yards *= pass_multiplier
        proj.receiving_tds *= pass_multiplier
        proj.receptions *= pass_multiplier
        
        return proj


class WRProjectionModel(UsageDrivenProjectionModel):
    """Wide receiver projection model."""
    
    def __init__(self):
        super().__init__("WR")
    
    def generate_projection(self, inputs: ProjectionInputs) -> ProjectionOutput:
        """Generate WR projections."""
        usage_factor = self.calculate_usage_factor(inputs.depth_chart_order, inputs.snap_share)
        
        # Base projections from recent performance
        base_proj = self._calculate_base_projections(inputs.recent_stats)
        
        # Apply usage factor
        base_proj.receiving_yards *= usage_factor
        base_proj.receiving_tds *= usage_factor
        base_proj.receptions *= usage_factor
        base_proj.rushing_yards *= usage_factor * 0.2  # WRs rush rarely
        base_proj.rushing_tds *= usage_factor * 0.1
        
        # Apply opponent defense adjustments
        base_proj = self._apply_defense_adjustments(base_proj, inputs.opponent_defense)
        
        # Apply injury adjustments
        base_proj = self.apply_injury_adjustment(base_proj, inputs.injury_status)
        
        return base_proj
    
    def _calculate_base_projections(self, recent_stats: List[Dict[str, Any]]) -> ProjectionOutput:
        """Calculate base projections from recent stats."""
        if not recent_stats:
            return ProjectionOutput()
        
        # Use last 4 games for WR projections
        recent_games = recent_stats[-4:] if len(recent_stats) >= 4 else recent_stats
        
        # Calculate averages with recent game weighting
        weights = [0.4, 0.3, 0.2, 0.1][:len(recent_games)]
        total_weight = sum(weights)
        
        proj = ProjectionOutput()
        
        for i, game in enumerate(recent_games):
            weight = weights[i] / total_weight
            proj.receiving_yards += game.get('receiving_yards', 0) * weight
            proj.receiving_tds += game.get('receiving_tds', 0) * weight
            proj.receptions += game.get('receptions', 0) * weight
            proj.rushing_yards += game.get('rushing_yards', 0) * weight
            proj.rushing_tds += game.get('rushing_tds', 0) * weight
        
        # Add regression to mean
        proj.receiving_yards *= 0.9
        proj.receiving_tds *= 0.95
        proj.receptions *= 0.9
        
        return proj
    
    def _apply_defense_adjustments(self, proj: ProjectionOutput, defense: Dict[str, float]) -> ProjectionOutput:
        """Apply opponent defense adjustments."""
        pass_def_rank = defense.get('pass_defense_rank', 16)
        
        pass_multiplier = 1.2 - (pass_def_rank - 1) * 0.0125
        
        proj.receiving_yards *= pass_multiplier
        proj.receiving_tds *= pass_multiplier
        proj.receptions *= pass_multiplier
        
        return proj


class TEProjectionModel(UsageDrivenProjectionModel):
    """Tight end projection model."""
    
    def __init__(self):
        super().__init__("TE")
    
    def generate_projection(self, inputs: ProjectionInputs) -> ProjectionOutput:
        """Generate TE projections."""
        usage_factor = self.calculate_usage_factor(inputs.depth_chart_order, inputs.snap_share)
        
        # Base projections from recent performance
        base_proj = self._calculate_base_projections(inputs.recent_stats)
        
        # Apply usage factor
        base_proj.receiving_yards *= usage_factor
        base_proj.receiving_tds *= usage_factor
        base_proj.receptions *= usage_factor
        
        # Apply opponent defense adjustments
        base_proj = self._apply_defense_adjustments(base_proj, inputs.opponent_defense)
        
        # Apply injury adjustments
        base_proj = self.apply_injury_adjustment(base_proj, inputs.injury_status)
        
        return base_proj
    
    def _calculate_base_projections(self, recent_stats: List[Dict[str, Any]]) -> ProjectionOutput:
        """Calculate base projections from recent stats."""
        if not recent_stats:
            return ProjectionOutput()
        
        # Use last 4 games for TE projections
        recent_games = recent_stats[-4:] if len(recent_stats) >= 4 else recent_stats
        
        # Calculate averages with recent game weighting
        weights = [0.4, 0.3, 0.2, 0.1][:len(recent_games)]
        total_weight = sum(weights)
        
        proj = ProjectionOutput()
        
        for i, game in enumerate(recent_games):
            weight = weights[i] / total_weight
            proj.receiving_yards += game.get('receiving_yards', 0) * weight
            proj.receiving_tds += game.get('receiving_tds', 0) * weight
            proj.receptions += game.get('receptions', 0) * weight
        
        # Add regression to mean
        proj.receiving_yards *= 0.9
        proj.receiving_tds *= 0.95
        proj.receptions *= 0.9
        
        return proj
    
    def _apply_defense_adjustments(self, proj: ProjectionOutput, defense: Dict[str, float]) -> ProjectionOutput:
        """Apply opponent defense adjustments."""
        pass_def_rank = defense.get('pass_defense_rank', 16)
        
        pass_multiplier = 1.2 - (pass_def_rank - 1) * 0.0125
        
        proj.receiving_yards *= pass_multiplier
        proj.receiving_tds *= pass_multiplier
        proj.receptions *= pass_multiplier
        
        return proj


class KProjectionModel(UsageDrivenProjectionModel):
    """Kicker projection model."""
    
    def __init__(self):
        super().__init__("K")
    
    def generate_projection(self, inputs: ProjectionInputs) -> ProjectionOutput:
        """Generate Kicker projections."""
        usage_factor = self.calculate_usage_factor(inputs.depth_chart_order, inputs.snap_share)
        
        # Base projections from recent performance
        base_proj = self._calculate_base_projections(inputs.recent_stats)
        
        # Apply usage factor
        base_proj.field_goals *= usage_factor
        base_proj.field_goal_attempts *= usage_factor
        base_proj.extra_points *= usage_factor
        base_proj.extra_point_attempts *= usage_factor
        
        # Apply team offense adjustments (more scoring = more kicks)
        base_proj = self._apply_offense_adjustments(base_proj, inputs.team_offense)
        
        # Apply injury adjustments
        base_proj = self.apply_injury_adjustment(base_proj, inputs.injury_status)
        
        return base_proj
    
    def _calculate_base_projections(self, recent_stats: List[Dict[str, Any]]) -> ProjectionOutput:
        """Calculate base projections from recent stats."""
        if not recent_stats:
            return ProjectionOutput()
        
        # Use last 4 games for K projections
        recent_games = recent_stats[-4:] if len(recent_stats) >= 4 else recent_stats
        
        # Calculate averages
        proj = ProjectionOutput()
        
        for game in recent_games:
            proj.field_goals += game.get('field_goals', 0)
            proj.field_goal_attempts += game.get('field_goal_attempts', 0)
            proj.extra_points += game.get('extra_points', 0)
            proj.extra_point_attempts += game.get('extra_point_attempts', 0)
        
        # Average over games
        num_games = len(recent_games)
        proj.field_goals /= num_games
        proj.field_goal_attempts /= num_games
        proj.extra_points /= num_games
        proj.extra_point_attempts /= num_games
        
        return proj
    
    def _apply_offense_adjustments(self, proj: ProjectionOutput, offense: Dict[str, float]) -> ProjectionOutput:
        """Apply team offense adjustments."""
        # Higher scoring offense = more field goals and extra points
        scoring_rank = offense.get('scoring_rank', 16)
        
        # Convert rank to multiplier (rank 1 = 1.3x, rank 32 = 0.7x)
        multiplier = 1.3 - (scoring_rank - 1) * 0.01875
        
        proj.field_goals *= multiplier
        proj.field_goal_attempts *= multiplier
        proj.extra_points *= multiplier
        proj.extra_point_attempts *= multiplier
        
        return proj


class ProjectionEngine:
    """Main projection engine that coordinates all position models."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.models = {
            "QB": QBProjectionModel(),
            "RB": RBProjectionModel(),
            "WR": WRProjectionModel(),
            "TE": TEProjectionModel(),
            "K": KProjectionModel(),
        }
    
    async def generate_player_projection(
        self, 
        gsis_id: str, 
        season: int, 
        week: int,
        position: str
    ) -> ProjectionOutput:
        """Generate projection for a specific player."""
        
        # Get recent stats (last 4 games)
        recent_stats = await self._get_recent_stats(gsis_id, season, week, 4)
        
        # Get depth chart information
        depth_order = await self._get_depth_chart_order(gsis_id, season, week)
        
        # Get snap share
        snap_share = await self._get_snap_share(gsis_id, season, week)
        
        # Get injury status
        injury_status = await self._get_injury_status(gsis_id, season, week)
        
        # Get opponent defense (placeholder - would need actual data)
        opponent_defense = {"pass_defense_rank": 16, "rush_defense_rank": 16}
        
        # Get team offense (placeholder - would need actual data)
        team_offense = {"scoring_rank": 16}
        
        # Create projection inputs
        inputs = ProjectionInputs(
            recent_stats=recent_stats,
            depth_chart_order=depth_order,
            snap_share=snap_share,
            injury_status=injury_status,
            opponent_defense=opponent_defense,
            team_offense=team_offense
        )
        
        # Generate projection using appropriate model
        model = self.models.get(position)
        if not model:
            return ProjectionOutput()
        
        return model.generate_projection(inputs)
    
    async def _get_recent_stats(self, gsis_id: str, season: int, week: int, num_games: int) -> List[Dict[str, Any]]:
        """Get recent stats for a player."""
        result = await self.db.execute(
            select(WeeklyStats).where(
                and_(
                    WeeklyStats.gsis_id == gsis_id,
                    WeeklyStats.season == season,
                    WeeklyStats.week < week
                )
            ).order_by(WeeklyStats.week.desc()).limit(num_games)
        )
        
        stats_records = result.scalars().all()
        return [record.stats for record in stats_records]
    
    async def _get_depth_chart_order(self, gsis_id: str, season: int, week: int) -> int:
        """Get depth chart order for a player."""
        result = await self.db.execute(
            select(DepthCharts).where(
                and_(
                    DepthCharts.gsis_id == gsis_id,
                    DepthCharts.season == season,
                    DepthCharts.week == week
                )
            )
        )
        
        depth_record = result.scalar_one_or_none()
        return depth_record.depth_order if depth_record else 3  # Default to 3rd string
    
    async def _get_snap_share(self, gsis_id: str, season: int, week: int) -> float:
        """Get snap share for a player."""
        result = await self.db.execute(
            select(WeeklyStats).where(
                and_(
                    WeeklyStats.gsis_id == gsis_id,
                    WeeklyStats.season == season,
                    WeeklyStats.week == week
                )
            )
        )
        
        stats_record = result.scalar_one_or_none()
        if stats_record:
            stats = stats_record.stats
            return stats.get('snap_pct', 50.0)  # Default to 50%
        
        return 50.0
    
    async def _get_injury_status(self, gsis_id: str, season: int, week: int) -> Optional[str]:
        """Get injury status for a player."""
        result = await self.db.execute(
            select(Injuries).where(
                and_(
                    Injuries.gsis_id == gsis_id,
                    Injuries.season == season,
                    Injuries.week == week
                )
            )
        )
        
        injury_record = result.scalar_one_or_none()
        return injury_record.status if injury_record else None
    
    async def save_projection(
        self, 
        gsis_id: str, 
        season: int, 
        week: int, 
        projection: ProjectionOutput,
        source: str = "internal"
    ) -> WeeklyProjections:
        """Save projection to database."""
        
        # Convert projection to dictionary
        proj_dict = {
            "passing_yards": projection.passing_yards,
            "passing_tds": projection.passing_tds,
            "passing_ints": projection.passing_ints,
            "rushing_yards": projection.rushing_yards,
            "rushing_tds": projection.rushing_tds,
            "receiving_yards": projection.receiving_yards,
            "receiving_tds": projection.receiving_tds,
            "receptions": projection.receptions,
            "fumbles_lost": projection.fumbles_lost,
            "field_goals": projection.field_goals,
            "field_goal_attempts": projection.field_goal_attempts,
            "extra_points": projection.extra_points,
            "extra_point_attempts": projection.extra_point_attempts,
        }
        
        # Check if projection already exists
        existing = await self.db.execute(
            select(WeeklyProjections).where(
                and_(
                    WeeklyProjections.gsis_id == gsis_id,
                    WeeklyProjections.season == season,
                    WeeklyProjections.week == week,
                    WeeklyProjections.source == source
                )
            )
        )
        existing_proj = existing.scalar_one_or_none()
        
        if existing_proj:
            # Update existing projection
            existing_proj.proj_json = json.dumps(proj_dict)
            existing_proj.confidence = projection.confidence
            existing_proj.updated_at = datetime.now(timezone.utc)
            return existing_proj
        else:
            # Create new projection
            new_proj = WeeklyProjections(
                gsis_id=gsis_id,
                season=season,
                week=week,
                source=source,
                proj_json=json.dumps(proj_dict),
                confidence=projection.confidence,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            self.db.add(new_proj)
            await self.db.commit()
            return new_proj
