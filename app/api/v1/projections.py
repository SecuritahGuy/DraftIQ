"""
Fantasy football projections API endpoints.
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.projection_engine import ProjectionEngine
from app.schemas.nfl_data import ProjectionRequest, ProjectionResponse

router = APIRouter()


@router.post("/generate/{gsis_id}/{season}/{week}")
async def generate_player_projection(
    gsis_id: str = Path(..., description="Player GSIS ID"),
    season: int = Path(..., description="NFL season year", ge=2020, le=2030),
    week: int = Path(..., description="Week number", ge=1, le=22),
    position: str = Query(..., description="Player position (QB, RB, WR, TE, K)"),
    save: bool = Query(True, description="Whether to save projection to database"),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Generate projection for a specific player.
    
    Args:
        gsis_id: Player GSIS ID
        season: NFL season year
        week: Week number
        position: Player position
        save: Whether to save projection to database
        
    Returns:
        Generated projection data
    """
    try:
        engine = ProjectionEngine(db)
        projection = await engine.generate_player_projection(gsis_id, season, week, position)
        
        if save:
            saved_proj = await engine.save_projection(gsis_id, season, week, projection)
            return {
                "success": True,
                "gsis_id": gsis_id,
                "season": season,
                "week": week,
                "position": position,
                "projection": {
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
                },
                "confidence": projection.confidence,
                "saved": True,
                "projection_id": saved_proj.gsis_id
            }
        else:
            return {
                "success": True,
                "gsis_id": gsis_id,
                "season": season,
                "week": week,
                "position": position,
                "projection": {
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
                },
                "confidence": projection.confidence,
                "saved": False
            }
        
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate projection: {str(e)}"
        )


@router.post("/generate/batch")
async def generate_batch_projections(
    players: List[Dict[str, Any]],
    season: int = Query(..., description="NFL season year", ge=2020, le=2030),
    week: int = Query(..., description="Week number", ge=1, le=22),
    save: bool = Query(True, description="Whether to save projections to database"),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Generate projections for multiple players.
    
    Args:
        players: List of player dictionaries with gsis_id and position
        season: NFL season year
        week: Week number
        save: Whether to save projections to database
        
    Returns:
        Batch projection results
    """
    try:
        engine = ProjectionEngine(db)
        results = []
        successful = 0
        failed = 0
        
        for player in players:
            try:
                gsis_id = player.get("gsis_id")
                position = player.get("position")
                
                if not gsis_id or not position:
                    results.append({
                        "gsis_id": gsis_id,
                        "position": position,
                        "success": False,
                        "error": "Missing gsis_id or position"
                    })
                    failed += 1
                    continue
                
                projection = await engine.generate_player_projection(gsis_id, season, week, position)
                
                if save:
                    saved_proj = await engine.save_projection(gsis_id, season, week, projection)
                    results.append({
                        "gsis_id": gsis_id,
                        "position": position,
                        "success": True,
                        "projection": {
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
                        },
                        "confidence": projection.confidence,
                        "saved": True
                    })
                else:
                    results.append({
                        "gsis_id": gsis_id,
                        "position": position,
                        "success": True,
                        "projection": {
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
                        },
                        "confidence": projection.confidence,
                        "saved": False
                    })
                
                successful += 1
                
            except Exception as e:
                results.append({
                    "gsis_id": player.get("gsis_id"),
                    "position": player.get("position"),
                    "success": False,
                    "error": str(e)
                })
                failed += 1
        
        return {
            "success": True,
            "season": season,
            "week": week,
            "total_players": len(players),
            "successful": successful,
            "failed": failed,
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate batch projections: {str(e)}"
        )


@router.get("/player/{gsis_id}/{season}/{week}")
async def get_player_projection(
    gsis_id: str = Path(..., description="Player GSIS ID"),
    season: int = Path(..., description="NFL season year", ge=2020, le=2030),
    week: int = Path(..., description="Week number", ge=1, le=22),
    source: str = Query("internal", description="Projection source"),
    db: AsyncSession = Depends(get_db)
) -> ProjectionResponse:
    """
    Get saved projection for a specific player.
    
    Args:
        gsis_id: Player GSIS ID
        season: NFL season year
        week: Week number
        source: Projection source
        
    Returns:
        Saved projection data
    """
    try:
        from app.models.nfl_data import WeeklyProjections
        from sqlalchemy import select, and_
        
        result = await db.execute(
            select(WeeklyProjections).where(
                and_(
                    WeeklyProjections.gsis_id == gsis_id,
                    WeeklyProjections.season == season,
                    WeeklyProjections.week == week,
                    WeeklyProjections.source == source
                )
            )
        )
        
        projection = result.scalar_one_or_none()
        
        if not projection:
            raise HTTPException(
                status_code=404,
                detail=f"No projection found for player {gsis_id} in season {season}, week {week}"
            )
        
        return ProjectionResponse(
            gsis_id=projection.gsis_id,
            season=projection.season,
            week=projection.week,
            source=projection.source,
            projections=projection.projections,
            confidence=projection.confidence,
            created_at=projection.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get projection: {str(e)}"
        )


@router.get("/league/{league_key}/{season}/{week}")
async def get_league_projections(
    league_key: str = Path(..., description="League key"),
    season: int = Path(..., description="NFL season year", ge=2020, le=2030),
    week: int = Path(..., description="Week number", ge=1, le=22),
    source: str = Query("internal", description="Projection source"),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get projections for all players in a league.
    
    Args:
        league_key: League key
        season: NFL season year
        week: Week number
        source: Projection source
        
    Returns:
        League projections data
    """
    try:
        from app.models.fantasy import LeaguePlayer
        from app.models.nfl_data import WeeklyProjections, PlayerIDMapping
        from sqlalchemy import select, and_, join
        
        # Get all players in the league
        players_result = await db.execute(
            select(LeaguePlayer).where(LeaguePlayer.league_key == league_key)
        )
        league_players = players_result.scalars().all()
        
        # Get projections for these players
        projections = []
        for league_player in league_players:
            # Get GSIS ID for this player
            mapping_result = await db.execute(
                select(PlayerIDMapping).where(
                    PlayerIDMapping.gsis_id.in_(
                        select(Player.gsis_id).where(Player.player_id_yahoo == league_player.player_id_yahoo)
                    )
                )
            )
            mapping = mapping_result.scalar_one_or_none()
            
            if mapping:
                # Get projection for this player
                proj_result = await db.execute(
                    select(WeeklyProjections).where(
                        and_(
                            WeeklyProjections.gsis_id == mapping.gsis_id,
                            WeeklyProjections.season == season,
                            WeeklyProjections.week == week,
                            WeeklyProjections.source == source
                        )
                    )
                )
                projection = proj_result.scalar_one_or_none()
                
                if projection:
                    projections.append({
                        "player_id_yahoo": league_player.player_id_yahoo,
                        "gsis_id": mapping.gsis_id,
                        "player_name": mapping.full_name,
                        "position": mapping.position,
                        "projection": projection.projections,
                        "confidence": projection.confidence,
                        "created_at": projection.created_at
                    })
        
        return {
            "league_key": league_key,
            "season": season,
            "week": week,
            "source": source,
            "total_projections": len(projections),
            "projections": projections
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get league projections: {str(e)}"
        )


@router.delete("/player/{gsis_id}/{season}/{week}")
async def delete_player_projection(
    gsis_id: str = Path(..., description="Player GSIS ID"),
    season: int = Path(..., description="NFL season year", ge=2020, le=2030),
    week: int = Path(..., description="Week number", ge=1, le=22),
    source: str = Query("internal", description="Projection source"),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Delete projection for a specific player.
    
    Args:
        gsis_id: Player GSIS ID
        season: NFL season year
        week: Week number
        source: Projection source
        
    Returns:
        Deletion result
    """
    try:
        from app.models.nfl_data import WeeklyProjections
        from sqlalchemy import select, and_, delete
        
        # Check if projection exists
        result = await db.execute(
            select(WeeklyProjections).where(
                and_(
                    WeeklyProjections.gsis_id == gsis_id,
                    WeeklyProjections.season == season,
                    WeeklyProjections.week == week,
                    WeeklyProjections.source == source
                )
            )
        )
        
        projection = result.scalar_one_or_none()
        
        if not projection:
            raise HTTPException(
                status_code=404,
                detail=f"No projection found for player {gsis_id} in season {season}, week {week}"
            )
        
        # Delete the projection
        await db.execute(
            delete(WeeklyProjections).where(
                and_(
                    WeeklyProjections.gsis_id == gsis_id,
                    WeeklyProjections.season == season,
                    WeeklyProjections.week == week,
                    WeeklyProjections.source == source
                )
            )
        )
        
        await db.commit()
        
        return {
            "success": True,
            "message": f"Projection deleted for player {gsis_id} in season {season}, week {week}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete projection: {str(e)}"
        )
