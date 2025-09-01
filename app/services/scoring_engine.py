"""
Fantasy football scoring engine for calculating points based on league rules.
"""

import json
import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from app.schemas.nfl_data import ScoringRule, ScoringSystem


class StatType(Enum):
    """Types of statistics that can be scored."""
    PASSING_YARDS = "passing_yards"
    PASSING_TDS = "passing_tds"
    PASSING_INTS = "passing_ints"
    RUSHING_YARDS = "rushing_yards"
    RUSHING_TDS = "rushing_tds"
    RECEIVING_YARDS = "receiving_yards"
    RECEIVING_TDS = "receiving_tds"
    RECEPTIONS = "receptions"
    FUMBLES_LOST = "fumbles_lost"
    FIELD_GOALS = "field_goals"
    FIELD_GOAL_ATTEMPTS = "field_goal_attempts"
    EXTRA_POINTS = "extra_points"
    EXTRA_POINT_ATTEMPTS = "extra_point_attempts"
    DEFENSIVE_INTS = "defensive_ints"
    DEFENSIVE_FUMBLES = "defensive_fumbles"
    DEFENSIVE_SACKS = "defensive_sacks"
    DEFENSIVE_TDS = "defensive_tds"
    DEFENSIVE_SAFETIES = "defensive_safeties"
    DEFENSIVE_POINTS_ALLOWED = "defensive_points_allowed"
    DEFENSIVE_YARDS_ALLOWED = "defensive_yards_allowed"


@dataclass
class ScoringRule:
    """Individual scoring rule configuration."""
    stat: str
    points: float
    threshold: Optional[float] = None
    max_points: Optional[float] = None
    tier_rules: Optional[List[Tuple[float, float, float]]] = None  # (min, max, points)


class YahooScoringParser:
    """Parser for Yahoo Fantasy scoring rules."""
    
    # Mapping from Yahoo stat names to our internal stat types
    YAHOO_STAT_MAPPING = {
        "Passing Yards": StatType.PASSING_YARDS,
        "Passing Touchdowns": StatType.PASSING_TDS,
        "Interceptions": StatType.PASSING_INTS,
        "Rushing Yards": StatType.RUSHING_YARDS,
        "Rushing Touchdowns": StatType.RUSHING_TDS,
        "Reception Yards": StatType.RECEIVING_YARDS,
        "Reception Touchdowns": StatType.RECEIVING_TDS,
        "Receptions": StatType.RECEPTIONS,
        "Fumbles Lost": StatType.FUMBLES_LOST,
        "Field Goals Made": StatType.FIELD_GOALS,
        "Field Goals Attempted": StatType.FIELD_GOAL_ATTEMPTS,
        "Extra Points Made": StatType.EXTRA_POINTS,
        "Extra Points Attempted": StatType.EXTRA_POINT_ATTEMPTS,
        "Interceptions": StatType.DEFENSIVE_INTS,
        "Fumbles Recovered": StatType.DEFENSIVE_FUMBLES,
        "Sacks": StatType.DEFENSIVE_SACKS,
        "Touchdowns": StatType.DEFENSIVE_TDS,
        "Safeties": StatType.DEFENSIVE_SAFETIES,
        "Points Allowed": StatType.DEFENSIVE_POINTS_ALLOWED,
        "Yards Allowed": StatType.DEFENSIVE_YARDS_ALLOWED,
    }
    
    def parse_yahoo_scoring(self, scoring_json: str) -> Dict[str, ScoringRule]:
        """
        Parse Yahoo scoring rules from JSON.
        
        Args:
            scoring_json: JSON string containing Yahoo scoring rules
            
        Returns:
            Dictionary mapping stat types to scoring rules
        """
        try:
            scoring_data = json.loads(scoring_json)
            rules = {}
            
            for stat_name, stat_config in scoring_data.items():
                if stat_name in self.YAHOO_STAT_MAPPING:
                    stat_type = self.YAHOO_STAT_MAPPING[stat_name]
                    
                    # Parse the scoring configuration
                    rule = self._parse_stat_config(stat_name, stat_config)
                    if rule:
                        rules[stat_type.value] = rule
            
            return rules
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            raise ValueError(f"Failed to parse Yahoo scoring rules: {str(e)}")
    
    def _parse_stat_config(self, stat_name: str, config: Dict[str, Any]) -> Optional[ScoringRule]:
        """Parse individual stat configuration."""
        try:
            # Yahoo typically stores scoring as "1" for 1 point per unit
            points = float(config.get("value", 0))
            
            # Check for tier-based scoring (e.g., "1-99 yards = 0.1 points, 100+ yards = 0.2 points")
            if "tiers" in config:
                tier_rules = []
                for tier in config["tiers"]:
                    min_val = tier.get("min", 0)
                    max_val = tier.get("max", float('inf'))
                    tier_points = tier.get("value", 0)
                    tier_rules.append((min_val, max_val, tier_points))
                
                return ScoringRule(
                    stat=stat_name,
                    points=points,
                    tier_rules=tier_rules
                )
            
            # Check for threshold-based scoring
            threshold = config.get("threshold")
            max_points = config.get("max_points")
            
            return ScoringRule(
                stat=stat_name,
                points=points,
                threshold=threshold,
                max_points=max_points
            )
            
        except (ValueError, TypeError) as e:
            print(f"Warning: Failed to parse stat config for {stat_name}: {str(e)}")
            return None


class ScoringEngine:
    """Fantasy football scoring engine."""
    
    def __init__(self, scoring_rules: Dict[str, ScoringRule]):
        self.scoring_rules = scoring_rules
    
    @classmethod
    def from_yahoo_scoring(cls, scoring_json: str) -> 'ScoringEngine':
        """Create scoring engine from Yahoo scoring rules."""
        parser = YahooScoringParser()
        rules = parser.parse_yahoo_scoring(scoring_json)
        return cls(rules)
    
    def calculate_fantasy_points(self, stats: Dict[str, Any]) -> Tuple[float, Dict[str, float]]:
        """
        Calculate fantasy points from player statistics.
        
        Args:
            stats: Dictionary of player statistics
            
        Returns:
            Tuple of (total_points, breakdown_by_stat)
        """
        total_points = 0.0
        breakdown = {}
        
        for stat_type, rule in self.scoring_rules.items():
            stat_value = self._get_stat_value(stats, stat_type)
            if stat_value is not None:
                points = self._calculate_stat_points(stat_value, rule)
                total_points += points
                breakdown[stat_type] = points
        
        return total_points, breakdown
    
    def _get_stat_value(self, stats: Dict[str, Any], stat_type: str) -> Optional[float]:
        """Extract stat value from stats dictionary."""
        # Map internal stat types to common stat field names
        stat_mapping = {
            StatType.PASSING_YARDS.value: ["passing_yards", "pass_yds", "passing_yds"],
            StatType.PASSING_TDS.value: ["passing_tds", "pass_td", "passing_td"],
            StatType.PASSING_INTS.value: ["passing_ints", "pass_int", "passing_int"],
            StatType.RUSHING_YARDS.value: ["rushing_yards", "rush_yds", "rushing_yds"],
            StatType.RUSHING_TDS.value: ["rushing_tds", "rush_td", "rushing_td"],
            StatType.RECEIVING_YARDS.value: ["receiving_yards", "rec_yds", "receiving_yds"],
            StatType.RECEIVING_TDS.value: ["receiving_tds", "rec_td", "receiving_td"],
            StatType.RECEPTIONS.value: ["receptions", "rec", "catches"],
            StatType.FUMBLES_LOST.value: ["fumbles_lost", "fumbles", "fum_lost"],
            StatType.FIELD_GOALS.value: ["field_goals", "fg_made", "fg"],
            StatType.FIELD_GOAL_ATTEMPTS.value: ["field_goal_attempts", "fg_att", "fg_attempts"],
            StatType.EXTRA_POINTS.value: ["extra_points", "xp_made", "xp"],
            StatType.EXTRA_POINT_ATTEMPTS.value: ["extra_point_attempts", "xp_att", "xp_attempts"],
        }
        
        possible_keys = stat_mapping.get(stat_type, [stat_type])
        
        for key in possible_keys:
            if key in stats:
                value = stats[key]
                if isinstance(value, (int, float)):
                    return float(value)
                elif isinstance(value, str) and value.replace('.', '').replace('-', '').isdigit():
                    return float(value)
        
        return None
    
    def _calculate_stat_points(self, value: float, rule: ScoringRule) -> float:
        """Calculate points for a specific stat value using the rule."""
        if rule.tier_rules:
            # Tier-based scoring
            for min_val, max_val, tier_points in rule.tier_rules:
                if min_val <= value <= max_val:
                    return tier_points * value if tier_points > 0 else tier_points
            return 0.0
        
        # Standard scoring
        points = rule.points * value
        
        # Apply threshold
        if rule.threshold is not None and value < rule.threshold:
            return 0.0
        
        # Apply max points
        if rule.max_points is not None:
            points = min(points, rule.max_points)
        
        return points
    
    def get_scoring_system(self) -> ScoringSystem:
        """Get the scoring system as a Pydantic model."""
        return ScoringSystem(
            passing_yards=ScoringRule(**self.scoring_rules.get(StatType.PASSING_YARDS.value, {}).__dict__) if StatType.PASSING_YARDS.value in self.scoring_rules else None,
            passing_tds=ScoringRule(**self.scoring_rules.get(StatType.PASSING_TDS.value, {}).__dict__) if StatType.PASSING_TDS.value in self.scoring_rules else None,
            passing_ints=ScoringRule(**self.scoring_rules.get(StatType.PASSING_INTS.value, {}).__dict__) if StatType.PASSING_INTS.value in self.scoring_rules else None,
            rushing_yards=ScoringRule(**self.scoring_rules.get(StatType.RUSHING_YARDS.value, {}).__dict__) if StatType.RUSHING_YARDS.value in self.scoring_rules else None,
            rushing_tds=ScoringRule(**self.scoring_rules.get(StatType.RUSHING_TDS.value, {}).__dict__) if StatType.RUSHING_TDS.value in self.scoring_rules else None,
            receiving_yards=ScoringRule(**self.scoring_rules.get(StatType.RECEIVING_YARDS.value, {}).__dict__) if StatType.RECEIVING_YARDS.value in self.scoring_rules else None,
            receiving_tds=ScoringRule(**self.scoring_rules.get(StatType.RECEIVING_TDS.value, {}).__dict__) if StatType.RECEIVING_TDS.value in self.scoring_rules else None,
            receptions=ScoringRule(**self.scoring_rules.get(StatType.RECEPTIONS.value, {}).__dict__) if StatType.RECEPTIONS.value in self.scoring_rules else None,
            fumbles_lost=ScoringRule(**self.scoring_rules.get(StatType.FUMBLES_LOST.value, {}).__dict__) if StatType.FUMBLES_LOST.value in self.scoring_rules else None,
            field_goals=ScoringRule(**self.scoring_rules.get(StatType.FIELD_GOALS.value, {}).__dict__) if StatType.FIELD_GOALS.value in self.scoring_rules else None,
            extra_points=ScoringRule(**self.scoring_rules.get(StatType.EXTRA_POINTS.value, {}).__dict__) if StatType.EXTRA_POINTS.value in self.scoring_rules else None,
        )


class FantasyPointsCalculator:
    """Service for calculating fantasy points for players."""
    
    def __init__(self, db):
        self.db = db
    
    async def calculate_player_points(self, gsis_id: str, season: int, week: int, league_key: str) -> Dict[str, Any]:
        """
        Calculate fantasy points for a player in a specific league.
        
        Args:
            gsis_id: Player GSIS ID
            season: NFL season year
            week: Week number
            league_key: League key for scoring rules
            
        Returns:
            Dictionary with calculated points and breakdown
        """
        from app.models.fantasy import League
        from app.models.nfl_data import WeeklyStats
        from sqlalchemy import select
        
        # Get league scoring rules
        league_result = await self.db.execute(
            select(League).where(League.league_key == league_key)
        )
        league = league_result.scalar_one_or_none()
        
        if not league:
            raise ValueError(f"League {league_key} not found")
        
        if not league.scoring_json:
            raise ValueError(f"No scoring rules found for league {league_key}")
        
        # Get player stats
        stats_result = await self.db.execute(
            select(WeeklyStats).where(
                WeeklyStats.gsis_id == gsis_id,
                WeeklyStats.season == season,
                WeeklyStats.week == week
            )
        )
        stats_record = stats_result.scalar_one_or_none()
        
        if not stats_record:
            raise ValueError(f"No stats found for player {gsis_id} in season {season}, week {week}")
        
        # Create scoring engine and calculate points
        scoring_engine = ScoringEngine.from_yahoo_scoring(league.scoring_json)
        total_points, breakdown = scoring_engine.calculate_fantasy_points(stats_record.stats)
        
        return {
            "gsis_id": gsis_id,
            "season": season,
            "week": week,
            "league_key": league_key,
            "fantasy_points": total_points,
            "scoring_breakdown": breakdown,
            "scoring_system": scoring_engine.get_scoring_system().dict()
        }
    
    async def calculate_team_points(self, team_key: str, season: int, week: int, league_key: str) -> Dict[str, Any]:
        """
        Calculate total fantasy points for a team's lineup.
        
        Args:
            team_key: Team key
            season: NFL season year
            week: Week number
            league_key: League key for scoring rules
            
        Returns:
            Dictionary with team total and player breakdowns
        """
        from app.models.fantasy import Roster
        from sqlalchemy import select
        
        # Get team roster for the week
        roster_result = await self.db.execute(
            select(Roster).where(
                Roster.team_key == team_key,
                Roster.week == week
            )
        )
        roster = roster_result.scalars().all()
        
        total_points = 0.0
        player_points = []
        
        for roster_slot in roster:
            if roster_slot.player_id_yahoo and roster_slot.is_starting:
                # Get player's GSIS ID from mapping
                from app.models.nfl_data import PlayerIDMapping
                mapping_result = await self.db.execute(
                    select(PlayerIDMapping).where(
                        PlayerIDMapping.gsis_id.in_(
                            select(Player.gsis_id).where(Player.player_id_yahoo == roster_slot.player_id_yahoo)
                        )
                    )
                )
                mapping = mapping_result.scalar_one_or_none()
                
                if mapping:
                    try:
                        player_result = await self.calculate_player_points(
                            mapping.gsis_id, season, week, league_key
                        )
                        total_points += player_result["fantasy_points"]
                        player_points.append({
                            "player_id_yahoo": roster_slot.player_id_yahoo,
                            "gsis_id": mapping.gsis_id,
                            "slot": roster_slot.slot,
                            "fantasy_points": player_result["fantasy_points"],
                            "scoring_breakdown": player_result["scoring_breakdown"]
                        })
                    except ValueError:
                        # Player stats not available
                        player_points.append({
                            "player_id_yahoo": roster_slot.player_id_yahoo,
                            "gsis_id": mapping.gsis_id,
                            "slot": roster_slot.slot,
                            "fantasy_points": 0.0,
                            "scoring_breakdown": {},
                            "error": "Stats not available"
                        })
        
        return {
            "team_key": team_key,
            "season": season,
            "week": week,
            "league_key": league_key,
            "total_fantasy_points": total_points,
            "player_points": player_points
        }
