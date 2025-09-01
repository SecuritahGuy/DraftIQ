"""
CSV import service for custom projections and data.
"""

import csv
import io
import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
import pandas as pd

from app.models.nfl_data import WeeklyProjections, PlayerIDMapping
from app.models.fantasy import Player


class CSVImportService:
    """Service for importing data from CSV files."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def import_projections_csv(
        self, 
        csv_content: str, 
        source: str = "csv",
        season: int = None,
        week: int = None
    ) -> Dict[str, Any]:
        """
        Import projections from CSV content.
        
        Expected CSV format:
        player_name,position,team,season,week,passing_yards,passing_tds,passing_ints,
        rushing_yards,rushing_tds,receiving_yards,receiving_tds,receptions,fumbles_lost,
        field_goals,field_goal_attempts,extra_points,extra_point_attempts,confidence
        
        Args:
            csv_content: CSV content as string
            source: Source identifier for projections
            season: Override season (if not in CSV)
            week: Override week (if not in CSV)
            
        Returns:
            Import results
        """
        try:
            # Parse CSV content
            df = pd.read_csv(io.StringIO(csv_content))
            
            # Validate required columns
            required_columns = ['player_name', 'position']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                return {
                    "success": False,
                    "error": f"Missing required columns: {missing_columns}"
                }
            
            # Process each row
            projections_created = 0
            projections_updated = 0
            errors = []
            
            for index, row in df.iterrows():
                try:
                    result = await self._process_projection_row(
                        row, source, season, week
                    )
                    
                    if result["success"]:
                        if result["created"]:
                            projections_created += 1
                        else:
                            projections_updated += 1
                    else:
                        errors.append({
                            "row": index + 1,
                            "player_name": row.get('player_name', 'Unknown'),
                            "error": result["error"]
                        })
                        
                except Exception as e:
                    errors.append({
                        "row": index + 1,
                        "player_name": row.get('player_name', 'Unknown'),
                        "error": str(e)
                    })
            
            await self.db.commit()
            
            return {
                "success": True,
                "projections_created": projections_created,
                "projections_updated": projections_updated,
                "total_processed": len(df),
                "errors": errors,
                "error_count": len(errors)
            }
            
        except Exception as e:
            await self.db.rollback()
            return {
                "success": False,
                "error": f"Failed to import CSV: {str(e)}"
            }
    
    async def _process_projection_row(
        self, 
        row: pd.Series, 
        source: str, 
        season_override: Optional[int], 
        week_override: Optional[int]
    ) -> Dict[str, Any]:
        """Process a single projection row."""
        
        # Extract player information
        player_name = str(row.get('player_name', '')).strip()
        position = str(row.get('position', '')).strip().upper()
        team = str(row.get('team', '')).strip()
        
        if not player_name or not position:
            return {
                "success": False,
                "error": "Missing player_name or position"
            }
        
        # Get season and week
        season = season_override or int(row.get('season', 0))
        week = week_override or int(row.get('week', 0))
        
        if not season or not week:
            return {
                "success": False,
                "error": "Missing season or week"
            }
        
        # Find player by name and position
        gsis_id = await self._find_player_gsis_id(player_name, position, team)
        
        if not gsis_id:
            return {
                "success": False,
                "error": f"Player not found: {player_name} ({position})"
            }
        
        # Extract projection data
        projection_data = {
            "passing_yards": float(row.get('passing_yards', 0)),
            "passing_tds": float(row.get('passing_tds', 0)),
            "passing_ints": float(row.get('passing_ints', 0)),
            "rushing_yards": float(row.get('rushing_yards', 0)),
            "rushing_tds": float(row.get('rushing_tds', 0)),
            "receiving_yards": float(row.get('receiving_yards', 0)),
            "receiving_tds": float(row.get('receiving_tds', 0)),
            "receptions": float(row.get('receptions', 0)),
            "fumbles_lost": float(row.get('fumbles_lost', 0)),
            "field_goals": float(row.get('field_goals', 0)),
            "field_goal_attempts": float(row.get('field_goal_attempts', 0)),
            "extra_points": float(row.get('extra_points', 0)),
            "extra_point_attempts": float(row.get('extra_point_attempts', 0)),
        }
        
        # Get confidence score
        confidence = float(row.get('confidence', 0.5))
        confidence = max(0.0, min(1.0, confidence))  # Clamp to 0-1 range
        
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
            existing_proj.proj_json = json.dumps(projection_data)
            existing_proj.confidence = confidence
            existing_proj.updated_at = datetime.now(timezone.utc)
            return {
                "success": True,
                "created": False,
                "gsis_id": gsis_id
            }
        else:
            # Create new projection
            new_proj = WeeklyProjections(
                gsis_id=gsis_id,
                season=season,
                week=week,
                source=source,
                proj_json=json.dumps(projection_data),
                confidence=confidence,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            self.db.add(new_proj)
            return {
                "success": True,
                "created": True,
                "gsis_id": gsis_id
            }
    
    async def _find_player_gsis_id(self, player_name: str, position: str, team: str = None) -> Optional[str]:
        """Find player GSIS ID by name, position, and optionally team."""
        
        # Try exact name match first
        result = await self.db.execute(
            select(PlayerIDMapping).where(
                and_(
                    PlayerIDMapping.full_name.ilike(f"%{player_name}%"),
                    PlayerIDMapping.position == position
                )
            )
        )
        mapping = result.scalar_one_or_none()
        
        if mapping:
            return mapping.gsis_id
        
        # Try partial name match
        name_parts = player_name.split()
        if len(name_parts) >= 2:
            first_name = name_parts[0]
            last_name = name_parts[-1]
            
            result = await self.db.execute(
                select(PlayerIDMapping).where(
                    and_(
                        PlayerIDMapping.first_name.ilike(f"%{first_name}%"),
                        PlayerIDMapping.last_name.ilike(f"%{last_name}%"),
                        PlayerIDMapping.position == position
                    )
                )
            )
            mapping = result.scalar_one_or_none()
            
            if mapping:
                return mapping.gsis_id
        
        # Try team-based matching if team is provided
        if team:
            result = await self.db.execute(
                select(PlayerIDMapping).where(
                    and_(
                        PlayerIDMapping.full_name.ilike(f"%{player_name}%"),
                        PlayerIDMapping.position == position,
                        PlayerIDMapping.team == team
                    )
                )
            )
            mapping = result.scalar_one_or_none()
            
            if mapping:
                return mapping.gsis_id
        
        return None
    
    async def get_csv_template(self) -> str:
        """Get CSV template for projections import."""
        template = """player_name,position,team,season,week,passing_yards,passing_tds,passing_ints,rushing_yards,rushing_tds,receiving_yards,receiving_tds,receptions,fumbles_lost,field_goals,field_goal_attempts,extra_points,extra_point_attempts,confidence
Josh Allen,QB,BUF,2024,1,250,2,1,25,0,0,0,0,0,0,0,0,0,0.8
Christian McCaffrey,RB,SF,2024,1,0,0,0,85,1,45,0,4,0,0,0,0,0,0.9
Cooper Kupp,WR,LAR,2024,1,0,0,0,0,0,95,1,7,0,0,0,0,0,0.85
Travis Kelce,TE,KC,2024,1,0,0,0,0,0,75,1,6,0,0,0,0,0,0.9
Justin Tucker,K,BAL,2024,1,0,0,0,0,0,0,0,0,0,2,3,3,3,0.95"""
        return template
    
    async def export_projections_csv(
        self, 
        season: int, 
        week: int, 
        source: str = "internal"
    ) -> str:
        """Export projections to CSV format."""
        
        # Get all projections for the specified season/week/source
        result = await self.db.execute(
            select(WeeklyProjections, PlayerIDMapping).join(
                PlayerIDMapping, WeeklyProjections.gsis_id == PlayerIDMapping.gsis_id
            ).where(
                and_(
                    WeeklyProjections.season == season,
                    WeeklyProjections.week == week,
                    WeeklyProjections.source == source
                )
            )
        )
        
        projections = result.all()
        
        # Create CSV content
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'player_name', 'position', 'team', 'season', 'week',
            'passing_yards', 'passing_tds', 'passing_ints',
            'rushing_yards', 'rushing_tds',
            'receiving_yards', 'receiving_tds', 'receptions',
            'fumbles_lost',
            'field_goals', 'field_goal_attempts',
            'extra_points', 'extra_point_attempts',
            'confidence'
        ])
        
        # Write data rows
        for proj, mapping in projections:
            proj_data = proj.projections
            
            writer.writerow([
                mapping.full_name,
                mapping.position,
                mapping.team or '',
                proj.season,
                proj.week,
                proj_data.get('passing_yards', 0),
                proj_data.get('passing_tds', 0),
                proj_data.get('passing_ints', 0),
                proj_data.get('rushing_yards', 0),
                proj_data.get('rushing_tds', 0),
                proj_data.get('receiving_yards', 0),
                proj_data.get('receiving_tds', 0),
                proj_data.get('receptions', 0),
                proj_data.get('fumbles_lost', 0),
                proj_data.get('field_goals', 0),
                proj_data.get('field_goal_attempts', 0),
                proj_data.get('extra_points', 0),
                proj_data.get('extra_point_attempts', 0),
                proj.confidence or 0.5
            ])
        
        return output.getvalue()
    
    async def validate_csv_format(self, csv_content: str) -> Dict[str, Any]:
        """Validate CSV format before import."""
        try:
            df = pd.read_csv(io.StringIO(csv_content))
            
            # Check required columns
            required_columns = ['player_name', 'position']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            # Check data types and values
            validation_errors = []
            
            if 'player_name' in df.columns:
                if df['player_name'].isna().any():
                    validation_errors.append("player_name column contains empty values")
            
            if 'position' in df.columns:
                valid_positions = ['QB', 'RB', 'WR', 'TE', 'K', 'DEF']
                invalid_positions = df[~df['position'].isin(valid_positions)]['position'].unique()
                if len(invalid_positions) > 0:
                    validation_errors.append(f"Invalid positions found: {list(invalid_positions)}")
            
            # Check numeric columns
            numeric_columns = [
                'passing_yards', 'passing_tds', 'passing_ints',
                'rushing_yards', 'rushing_tds',
                'receiving_yards', 'receiving_tds', 'receptions',
                'fumbles_lost', 'field_goals', 'field_goal_attempts',
                'extra_points', 'extra_point_attempts', 'confidence'
            ]
            
            for col in numeric_columns:
                if col in df.columns:
                    try:
                        pd.to_numeric(df[col], errors='coerce')
                    except:
                        validation_errors.append(f"Column {col} contains non-numeric values")
            
            return {
                "valid": len(validation_errors) == 0 and len(missing_columns) == 0,
                "missing_columns": missing_columns,
                "validation_errors": validation_errors,
                "row_count": len(df),
                "columns": list(df.columns)
            }
            
        except Exception as e:
            return {
                "valid": False,
                "error": f"Failed to parse CSV: {str(e)}"
            }
