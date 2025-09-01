"""
Data synchronization and player mapping API endpoints.
"""

from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.data_sync import DataSyncService
from app.services.player_mapping import PlayerMappingService
from app.schemas.yahoo import LeagueSyncResponse

router = APIRouter(prefix="/data", tags=["data-sync"])


@router.post("/sync/league/{league_key}", response_model=LeagueSyncResponse)
async def sync_league_data(
    league_key: str = Path(..., description="Yahoo league key to sync"),
    db: AsyncSession = Depends(get_db)
) -> LeagueSyncResponse:
    """
    Sync league data from Yahoo API to local database.
    
    This endpoint will:
    1. Fetch league data from Yahoo API
    2. Store/update league, teams, players, and rosters in local database
    3. Implement caching to avoid unnecessary API calls
    """
    try:
        # TODO: Implement actual Yahoo API integration
        # For now, return mock response
        
        sync_service = DataSyncService(db)
        
        # Mock sync operation
        teams_synced = 12
        players_synced = 180
        draft_picks_synced = 144
        
        return LeagueSyncResponse(
            success=True,
            league_key=league_key,
            message="League data synced successfully",
            teams_synced=teams_synced,
            players_synced=players_synced,
            draft_picks_synced=draft_picks_synced
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to sync league data: {str(e)}"
        )


@router.post("/mapping/import-nfl-ids")
async def import_nfl_data_ids(
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Import player ID mappings from nfl_data_py.
    
    This endpoint uses nfl_data_py.import_ids() to populate our
    player_id_mapping table with GSIS, PFR, and ESPN IDs.
    """
    try:
        mapping_service = PlayerMappingService(db)
        result = await mapping_service.import_nfl_data_ids()
        
        if result["success"]:
            return {
                "success": True,
                "message": "NFL data IDs imported successfully",
                "mappings_created": result["mappings_created"],
                "mappings_updated": result["mappings_updated"],
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
            detail=f"Failed to import NFL data IDs: {str(e)}"
        )


@router.get("/mapping/yahoo-to-gsis/{yahoo_player_id}")
async def map_yahoo_to_gsis(
    yahoo_player_id: str = Path(..., description="Yahoo player ID"),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Map Yahoo player ID to GSIS ID.
    
    Args:
        yahoo_player_id: Yahoo player ID
        
    Returns:
        Mapping information including GSIS ID if found
    """
    try:
        mapping_service = PlayerMappingService(db)
        gsis_id = await mapping_service.map_yahoo_to_gsis(yahoo_player_id)
        
        return {
            "yahoo_player_id": yahoo_player_id,
            "gsis_id": gsis_id,
            "mapped": gsis_id is not None
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to map Yahoo to GSIS ID: {str(e)}"
        )


@router.get("/mapping/gsis-to-yahoo/{gsis_id}")
async def map_gsis_to_yahoo(
    gsis_id: str = Path(..., description="GSIS ID"),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Map GSIS ID to Yahoo player ID.
    
    Args:
        gsis_id: GSIS ID
        
    Returns:
        Mapping information including Yahoo player ID if found
    """
    try:
        mapping_service = PlayerMappingService(db)
        yahoo_player_id = await mapping_service.map_gsis_to_yahoo(gsis_id)
        
        return {
            "gsis_id": gsis_id,
            "yahoo_player_id": yahoo_player_id,
            "mapped": yahoo_player_id is not None
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to map GSIS to Yahoo ID: {str(e)}"
        )


@router.get("/mapping/search")
async def search_player_mappings(
    full_name: str = Query(..., description="Player's full name"),
    position: str = Query(None, description="Player position (optional filter)"),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Search for player mappings by name.
    
    Args:
        full_name: Player's full name
        position: Player position (optional filter)
        
    Returns:
        List of matching player mappings
    """
    try:
        mapping_service = PlayerMappingService(db)
        mappings = await mapping_service.find_player_by_name(full_name, position)
        
        return {
            "full_name": full_name,
            "position": position,
            "mappings": mappings,
            "count": len(mappings)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to search player mappings: {str(e)}"
        )


@router.get("/mapping/unmapped-yahoo-players")
async def get_unmapped_yahoo_players(
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get Yahoo players that don't have GSIS ID mappings.
    
    Returns:
        List of unmapped Yahoo players
    """
    try:
        mapping_service = PlayerMappingService(db)
        unmapped_players = await mapping_service.get_unmapped_yahoo_players()
        
        return {
            "unmapped_players": [
                {
                    "player_id_yahoo": player.player_id_yahoo,
                    "full_name": player.full_name,
                    "position": player.position,
                    "team": player.team
                }
                for player in unmapped_players
            ],
            "count": len(unmapped_players)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get unmapped Yahoo players: {str(e)}"
        )


@router.get("/mapping/suggest/{yahoo_player_id}")
async def suggest_mappings(
    yahoo_player_id: str = Path(..., description="Yahoo player ID"),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Suggest potential mappings for a Yahoo player.
    
    Args:
        yahoo_player_id: Yahoo player ID
        
    Returns:
        List of potential mappings with confidence scores
    """
    try:
        mapping_service = PlayerMappingService(db)
        
        # Get the Yahoo player
        from app.models.fantasy import Player
        from sqlalchemy import select
        
        stmt = select(Player).where(Player.player_id_yahoo == yahoo_player_id)
        result = await db.execute(stmt)
        yahoo_player = result.scalar_one_or_none()
        
        if not yahoo_player:
            raise HTTPException(
                status_code=404,
                detail=f"Yahoo player with ID {yahoo_player_id} not found"
            )
        
        suggestions = await mapping_service.suggest_mappings(yahoo_player)
        
        return {
            "yahoo_player": {
                "player_id_yahoo": yahoo_player.player_id_yahoo,
                "full_name": yahoo_player.full_name,
                "position": yahoo_player.position,
                "team": yahoo_player.team
            },
            "suggestions": suggestions,
            "count": len(suggestions)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to suggest mappings: {str(e)}"
        )


@router.get("/cache/league/{league_key}")
async def get_cached_league_data(
    league_key: str = Path(..., description="Yahoo league key"),
    max_age_hours: int = Query(24, description="Maximum age of cached data in hours"),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get cached league data if it's recent enough.
    
    Args:
        league_key: League key
        max_age_hours: Maximum age of cached data in hours
        
    Returns:
        Cached league data or empty result if too old
    """
    try:
        sync_service = DataSyncService(db)
        cached_data = await sync_service.get_cached_league_data(league_key, max_age_hours)
        
        if cached_data:
            return {
                "cached": True,
                "league_key": league_key,
                "data": {
                    "league": {
                        "league_key": cached_data["league"].league_key,
                        "name": cached_data["league"].name,
                        "season": cached_data["league"].season,
                        "updated_at": cached_data["league"].updated_at.isoformat()
                    },
                    "teams_count": len(cached_data["teams"]),
                    "players_count": len(cached_data["players"])
                }
            }
        else:
            return {
                "cached": False,
                "league_key": league_key,
                "message": "No recent cached data found"
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get cached league data: {str(e)}"
        )
