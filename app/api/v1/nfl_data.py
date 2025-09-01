"""
NFL data ingestion API endpoints.
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.nfl_data_ingestion import NFLDataIngestionService

router = APIRouter()


@router.post("/import/weekly-stats/{season}")
async def import_weekly_stats(
    season: int = Path(..., description="NFL season year", ge=2020, le=2030),
    week: Optional[int] = Query(None, description="Specific week to import", ge=1, le=22),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Import weekly statistics from nfl_data_py.
    
    Args:
        season: NFL season year (2020-2030)
        week: Specific week to import (1-22, optional)
        
    Returns:
        Import results with counts of created/updated records
    """
    try:
        service = NFLDataIngestionService(db)
        result = await service.import_weekly_stats(season, week)
        
        if result["success"]:
            return {
                "success": True,
                "message": f"Weekly stats imported successfully for season {season}" + (f", week {week}" if week else ""),
                "stats_created": result["stats_created"],
                "stats_updated": result["stats_updated"],
                "total_processed": result["total_processed"]
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=result["error"]
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to import weekly stats: {str(e)}"
        )


@router.post("/import/injuries/{season}")
async def import_injuries(
    season: int = Path(..., description="NFL season year", ge=2020, le=2030),
    week: Optional[int] = Query(None, description="Specific week to import", ge=1, le=22),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Import injury data from nfl_data_py.
    
    Args:
        season: NFL season year (2020-2030)
        week: Specific week to import (1-22, optional)
        
    Returns:
        Import results with counts of created/updated records
    """
    try:
        service = NFLDataIngestionService(db)
        result = await service.import_injuries(season, week)
        
        if result["success"]:
            return {
                "success": True,
                "message": f"Injury data imported successfully for season {season}" + (f", week {week}" if week else ""),
                "injuries_created": result["injuries_created"],
                "injuries_updated": result["injuries_updated"],
                "total_processed": result["total_processed"]
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=result["error"]
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to import injuries: {str(e)}"
        )


@router.post("/import/depth-charts/{season}")
async def import_depth_charts(
    season: int = Path(..., description="NFL season year", ge=2020, le=2030),
    week: Optional[int] = Query(None, description="Specific week to import", ge=1, le=22),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Import depth chart data from nfl_data_py.
    
    Args:
        season: NFL season year (2020-2030)
        week: Specific week to import (1-22, optional)
        
    Returns:
        Import results with counts of created/updated records
    """
    try:
        service = NFLDataIngestionService(db)
        result = await service.import_depth_charts(season, week)
        
        if result["success"]:
            return {
                "success": True,
                "message": f"Depth chart data imported successfully for season {season}" + (f", week {week}" if week else ""),
                "charts_created": result["charts_created"],
                "charts_updated": result["charts_updated"],
                "total_processed": result["total_processed"]
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=result["error"]
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to import depth charts: {str(e)}"
        )


@router.post("/import/snap-counts/{season}")
async def import_snap_counts(
    season: int = Path(..., description="NFL season year", ge=2020, le=2030),
    week: Optional[int] = Query(None, description="Specific week to import", ge=1, le=22),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Import snap count data from nfl_data_py.
    
    Args:
        season: NFL season year (2020-2030)
        week: Specific week to import (1-22, optional)
        
    Returns:
        Import results with counts of updated records
    """
    try:
        service = NFLDataIngestionService(db)
        result = await service.import_snap_counts(season, week)
        
        if result["success"]:
            return {
                "success": True,
                "message": f"Snap count data imported successfully for season {season}" + (f", week {week}" if week else ""),
                "stats_updated": result["stats_updated"],
                "total_processed": result["total_processed"]
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=result["error"]
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to import snap counts: {str(e)}"
        )


@router.post("/import/all/{season}")
async def import_all_nfl_data(
    season: int = Path(..., description="NFL season year", ge=2020, le=2030),
    week: Optional[int] = Query(None, description="Specific week to import", ge=1, le=22),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Import all NFL data (weekly stats, injuries, depth charts, snap counts) from nfl_data_py.
    
    Args:
        season: NFL season year (2020-2030)
        week: Specific week to import (1-22, optional)
        
    Returns:
        Combined import results for all data types
    """
    try:
        service = NFLDataIngestionService(db)
        
        # Import all data types
        weekly_result = await service.import_weekly_stats(season, week)
        injury_result = await service.import_injuries(season, week)
        depth_result = await service.import_depth_charts(season, week)
        snap_result = await service.import_snap_counts(season, week)
        
        # Check if any imports failed
        failed_imports = []
        if not weekly_result["success"]:
            failed_imports.append(f"Weekly stats: {weekly_result['error']}")
        if not injury_result["success"]:
            failed_imports.append(f"Injuries: {injury_result['error']}")
        if not depth_result["success"]:
            failed_imports.append(f"Depth charts: {depth_result['error']}")
        if not snap_result["success"]:
            failed_imports.append(f"Snap counts: {snap_result['error']}")
        
        if failed_imports:
            return {
                "success": False,
                "message": "Some imports failed",
                "failed_imports": failed_imports,
                "weekly_stats": weekly_result,
                "injuries": injury_result,
                "depth_charts": depth_result,
                "snap_counts": snap_result
            }
        
        # All imports successful
        return {
            "success": True,
            "message": f"All NFL data imported successfully for season {season}" + (f", week {week}" if week else ""),
            "weekly_stats": weekly_result,
            "injuries": injury_result,
            "depth_charts": depth_result,
            "snap_counts": snap_result
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to import NFL data: {str(e)}"
        )


@router.get("/stats/{gsis_id}/{season}/{week}")
async def get_weekly_stats(
    gsis_id: str = Path(..., description="Player GSIS ID"),
    season: int = Path(..., description="NFL season year", ge=2020, le=2030),
    week: int = Path(..., description="Week number", ge=1, le=22),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get weekly statistics for a specific player.
    
    Args:
        gsis_id: Player GSIS ID
        season: NFL season year
        week: Week number
        
    Returns:
        Player's weekly statistics
    """
    try:
        service = NFLDataIngestionService(db)
        stats = await service.get_weekly_stats(gsis_id, season, week)
        
        if not stats:
            raise HTTPException(
                status_code=404,
                detail=f"No stats found for player {gsis_id} in season {season}, week {week}"
            )
        
        return {
            "gsis_id": stats.gsis_id,
            "season": stats.season,
            "week": stats.week,
            "team": stats.team,
            "opponent": stats.opponent,
            "game_date": stats.game_date,
            "stats": stats.stats,
            "fantasy_points": stats.fantasy_points
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get weekly stats: {str(e)}"
        )


@router.get("/injuries/{gsis_id}/{season}/{week}")
async def get_player_injuries(
    gsis_id: str = Path(..., description="Player GSIS ID"),
    season: int = Path(..., description="NFL season year", ge=2020, le=2030),
    week: int = Path(..., description="Week number", ge=1, le=22),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get injury information for a specific player.
    
    Args:
        gsis_id: Player GSIS ID
        season: NFL season year
        week: Week number
        
    Returns:
        Player's injury information
    """
    try:
        service = NFLDataIngestionService(db)
        injury = await service.get_player_injuries(gsis_id, season, week)
        
        if not injury:
            raise HTTPException(
                status_code=404,
                detail=f"No injury data found for player {gsis_id} in season {season}, week {week}"
            )
        
        return {
            "gsis_id": injury.gsis_id,
            "season": injury.season,
            "week": injury.week,
            "status": injury.status,
            "report": injury.report,
            "practice_status": injury.practice_status,
            "team": injury.team,
            "position": injury.position,
            "is_out": injury.is_out,
            "is_questionable": injury.is_questionable
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get injury data: {str(e)}"
        )


@router.get("/depth-chart/{team}/{season}/{week}")
async def get_team_depth_chart(
    team: str = Path(..., description="Team abbreviation"),
    season: int = Path(..., description="NFL season year", ge=2020, le=2030),
    week: int = Path(..., description="Week number", ge=1, le=22),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get depth chart for a specific team.
    
    Args:
        team: Team abbreviation (e.g., "KC", "NE")
        season: NFL season year
        week: Week number
        
    Returns:
        Team's depth chart organized by position
    """
    try:
        service = NFLDataIngestionService(db)
        depth_charts = await service.get_team_depth_chart(team, season, week)
        
        if not depth_charts:
            raise HTTPException(
                status_code=404,
                detail=f"No depth chart found for team {team} in season {season}, week {week}"
            )
        
        # Organize by position
        chart_by_position = {}
        for chart in depth_charts:
            if chart.position not in chart_by_position:
                chart_by_position[chart.position] = []
            chart_by_position[chart.position].append({
                "gsis_id": chart.gsis_id,
                "depth_order": chart.depth_order,
                "role": chart.role,
                "is_starter": chart.is_starter
            })
        
        return {
            "team": team,
            "season": season,
            "week": week,
            "depth_chart": chart_by_position
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get depth chart: {str(e)}"
        )
