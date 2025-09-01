"""
NFL data ingestion service using nfl_data_py.
"""

import asyncio
import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
import pandas as pd

from app.models.nfl_data import WeeklyStats, WeeklyProjections, Injuries, DepthCharts, PlayerIDMapping
from app.models.fantasy import Player


class NFLDataIngestionService:
    """Service for ingesting NFL data from nfl_data_py."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def import_weekly_stats(self, season: int, week: Optional[int] = None) -> Dict[str, Any]:
        """
        Import weekly statistics from nfl_data_py.
        
        Args:
            season: NFL season year
            week: Specific week to import (None for all weeks)
            
        Returns:
            Dictionary with import results
        """
        try:
            import nfl_data_py as nfl
            
            # Import weekly data
            if week:
                weekly_data = nfl.import_weekly_data([season], [week])
            else:
                weekly_data = nfl.import_weekly_data([season])
            
            if weekly_data.empty:
                return {
                    "success": False,
                    "error": f"No weekly data found for season {season}" + (f", week {week}" if week else "")
                }
            
            # Process and store data
            stats_created = 0
            stats_updated = 0
            
            for _, row in weekly_data.iterrows():
                gsis_id = row.get('player_id')
                if not gsis_id:
                    continue
                
                # Convert row to stats dictionary
                stats_dict = row.to_dict()
                # Remove non-stat fields
                stats_dict.pop('player_id', None)
                stats_dict.pop('season', None)
                stats_dict.pop('week', None)
                stats_dict.pop('team', None)
                stats_dict.pop('opponent', None)
                stats_dict.pop('game_date', None)
                
                # Check if record exists
                existing = await self.db.execute(
                    select(WeeklyStats).where(
                        WeeklyStats.gsis_id == gsis_id,
                        WeeklyStats.season == season,
                        WeeklyStats.week == row.get('week', 1)
                    )
                )
                existing_stats = existing.scalar_one_or_none()
                
                if existing_stats:
                    # Update existing record
                    existing_stats.stat_json = json.dumps(stats_dict)
                    existing_stats.team = row.get('team', '')
                    existing_stats.opponent = row.get('opponent')
                    existing_stats.game_date = row.get('game_date')
                    existing_stats.updated_at = datetime.now(timezone.utc)
                    stats_updated += 1
                else:
                    # Create new record
                    new_stats = WeeklyStats(
                        gsis_id=gsis_id,
                        season=season,
                        week=row.get('week', 1),
                        stat_json=json.dumps(stats_dict),
                        team=row.get('team', ''),
                        opponent=row.get('opponent'),
                        game_date=row.get('game_date'),
                        created_at=datetime.now(timezone.utc),
                        updated_at=datetime.now(timezone.utc)
                    )
                    self.db.add(new_stats)
                    stats_created += 1
            
            await self.db.commit()
            
            return {
                "success": True,
                "stats_created": stats_created,
                "stats_updated": stats_updated,
                "total_processed": len(weekly_data)
            }
            
        except ImportError:
            return {
                "success": False,
                "error": "nfl_data_py not installed. Install with: pip install nfl_data_py"
            }
        except Exception as e:
            await self.db.rollback()
            return {
                "success": False,
                "error": f"Failed to import weekly stats: {str(e)}"
            }
    
    async def import_injuries(self, season: int, week: Optional[int] = None) -> Dict[str, Any]:
        """
        Import injury data from nfl_data_py.
        
        Args:
            season: NFL season year
            week: Specific week to import (None for all weeks)
            
        Returns:
            Dictionary with import results
        """
        try:
            import nfl_data_py as nfl
            
            # Import injury data
            injury_data = nfl.import_injuries([season])
            
            if injury_data.empty:
                return {
                    "success": False,
                    "error": f"No injury data found for season {season}"
                }
            
            # Filter by week if specified
            if week:
                injury_data = injury_data[injury_data['week'] == week]
            
            # Process and store data
            injuries_created = 0
            injuries_updated = 0
            
            for _, row in injury_data.iterrows():
                gsis_id = row.get('player_id')
                if not gsis_id:
                    continue
                
                # Check if record exists
                existing = await self.db.execute(
                    select(Injuries).where(
                        Injuries.gsis_id == gsis_id,
                        Injuries.season == season,
                        Injuries.week == row.get('week', 1)
                    )
                )
                existing_injury = existing.scalar_one_or_none()
                
                if existing_injury:
                    # Update existing record
                    existing_injury.status = row.get('status', '')
                    existing_injury.report = row.get('report')
                    existing_injury.practice_status = row.get('practice_status')
                    existing_injury.team = row.get('team', '')
                    existing_injury.position = row.get('position', '')
                    existing_injury.updated_at = datetime.now(timezone.utc)
                    injuries_updated += 1
                else:
                    # Create new record
                    new_injury = Injuries(
                        gsis_id=gsis_id,
                        season=season,
                        week=row.get('week', 1),
                        status=row.get('status', ''),
                        report=row.get('report'),
                        practice_status=row.get('practice_status'),
                        team=row.get('team', ''),
                        position=row.get('position', ''),
                        created_at=datetime.now(timezone.utc),
                        updated_at=datetime.now(timezone.utc)
                    )
                    self.db.add(new_injury)
                    injuries_created += 1
            
            await self.db.commit()
            
            return {
                "success": True,
                "injuries_created": injuries_created,
                "injuries_updated": injuries_updated,
                "total_processed": len(injury_data)
            }
            
        except ImportError:
            return {
                "success": False,
                "error": "nfl_data_py not installed. Install with: pip install nfl_data_py"
            }
        except Exception as e:
            await self.db.rollback()
            return {
                "success": False,
                "error": f"Failed to import injuries: {str(e)}"
            }
    
    async def import_depth_charts(self, season: int, week: Optional[int] = None) -> Dict[str, Any]:
        """
        Import depth chart data from nfl_data_py.
        
        Args:
            season: NFL season year
            week: Specific week to import (None for all weeks)
            
        Returns:
            Dictionary with import results
        """
        try:
            import nfl_data_py as nfl
            
            # Import depth chart data
            depth_data = nfl.import_depth_charts([season])
            
            if depth_data.empty:
                return {
                    "success": False,
                    "error": f"No depth chart data found for season {season}"
                }
            
            # Filter by week if specified
            if week:
                depth_data = depth_data[depth_data['week'] == week]
            
            # Process and store data
            charts_created = 0
            charts_updated = 0
            
            for _, row in depth_data.iterrows():
                team = row.get('team')
                position = row.get('position')
                week_num = row.get('week', 1)
                
                if not all([team, position]):
                    continue
                
                # Check if record exists
                existing = await self.db.execute(
                    select(DepthCharts).where(
                        DepthCharts.team == team,
                        DepthCharts.week == week_num,
                        DepthCharts.season == season,
                        DepthCharts.position == position
                    )
                )
                existing_chart = existing.scalar_one_or_none()
                
                if existing_chart:
                    # Update existing record
                    existing_chart.gsis_id = row.get('player_id', '')
                    existing_chart.depth_order = row.get('depth_order', 1)
                    existing_chart.role = row.get('role')
                    existing_chart.updated_at = datetime.now(timezone.utc)
                    charts_updated += 1
                else:
                    # Create new record
                    new_chart = DepthCharts(
                        team=team,
                        week=week_num,
                        season=season,
                        position=position,
                        gsis_id=row.get('player_id', ''),
                        depth_order=row.get('depth_order', 1),
                        role=row.get('role'),
                        created_at=datetime.now(timezone.utc),
                        updated_at=datetime.now(timezone.utc)
                    )
                    self.db.add(new_chart)
                    charts_created += 1
            
            await self.db.commit()
            
            return {
                "success": True,
                "charts_created": charts_created,
                "charts_updated": charts_updated,
                "total_processed": len(depth_data)
            }
            
        except ImportError:
            return {
                "success": False,
                "error": "nfl_data_py not installed. Install with: pip install nfl_data_py"
            }
        except Exception as e:
            await self.db.rollback()
            return {
                "success": False,
                "error": f"Failed to import depth charts: {str(e)}"
            }
    
    async def import_snap_counts(self, season: int, week: Optional[int] = None) -> Dict[str, Any]:
        """
        Import snap count data from nfl_data_py.
        
        Args:
            season: NFL season year
            week: Specific week to import (None for all weeks)
            
        Returns:
            Dictionary with import results
        """
        try:
            import nfl_data_py as nfl
            
            # Import snap count data
            snap_data = nfl.import_snap_counts([season])
            
            if snap_data.empty:
                return {
                    "success": False,
                    "error": f"No snap count data found for season {season}"
                }
            
            # Filter by week if specified
            if week:
                snap_data = snap_data[snap_data['week'] == week]
            
            # For now, we'll store snap counts in the weekly_stats table
            # as additional statistics. In the future, we might create a separate table.
            stats_updated = 0
            
            for _, row in snap_data.iterrows():
                gsis_id = row.get('player_id')
                if not gsis_id:
                    continue
                
                # Find existing weekly stats record
                existing = await self.db.execute(
                    select(WeeklyStats).where(
                        WeeklyStats.gsis_id == gsis_id,
                        WeeklyStats.season == season,
                        WeeklyStats.week == row.get('week', 1)
                    )
                )
                existing_stats = existing.scalar_one_or_none()
                
                if existing_stats:
                    # Update existing stats with snap count data
                    stats_dict = existing_stats.stats
                    stats_dict.update({
                        'snap_counts': row.get('snap_counts', 0),
                        'snap_pct': row.get('snap_pct', 0.0),
                        'offensive_snaps': row.get('offensive_snaps', 0),
                        'defensive_snaps': row.get('defensive_snaps', 0),
                        'special_teams_snaps': row.get('special_teams_snaps', 0)
                    })
                    existing_stats.stat_json = json.dumps(stats_dict)
                    existing_stats.updated_at = datetime.now(timezone.utc)
                    stats_updated += 1
            
            await self.db.commit()
            
            return {
                "success": True,
                "stats_updated": stats_updated,
                "total_processed": len(snap_data)
            }
            
        except ImportError:
            return {
                "success": False,
                "error": "nfl_data_py not installed. Install with: pip install nfl_data_py"
            }
        except Exception as e:
            await self.db.rollback()
            return {
                "success": False,
                "error": f"Failed to import snap counts: {str(e)}"
            }
    
    async def get_weekly_stats(self, gsis_id: str, season: int, week: int) -> Optional[WeeklyStats]:
        """Get weekly stats for a specific player."""
        result = await self.db.execute(
            select(WeeklyStats).where(
                WeeklyStats.gsis_id == gsis_id,
                WeeklyStats.season == season,
                WeeklyStats.week == week
            )
        )
        return result.scalar_one_or_none()
    
    async def get_player_injuries(self, gsis_id: str, season: int, week: int) -> Optional[Injuries]:
        """Get injury information for a specific player."""
        result = await self.db.execute(
            select(Injuries).where(
                Injuries.gsis_id == gsis_id,
                Injuries.season == season,
                Injuries.week == week
            )
        )
        return result.scalar_one_or_none()
    
    async def get_team_depth_chart(self, team: str, season: int, week: int) -> List[DepthCharts]:
        """Get depth chart for a specific team."""
        result = await self.db.execute(
            select(DepthCharts).where(
                DepthCharts.team == team,
                DepthCharts.season == season,
                DepthCharts.week == week
            ).order_by(DepthCharts.position, DepthCharts.depth_order)
        )
        return result.scalars().all()
