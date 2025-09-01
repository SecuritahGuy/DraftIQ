"""
Fantasy football scoring API endpoints.
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.scoring_engine import FantasyPointsCalculator, ScoringEngine
from app.schemas.nfl_data import FantasyPointsResponse, ScoringSystem

router = APIRouter()


@router.get("/points/player/{gsis_id}/{season}/{week}")
async def calculate_player_fantasy_points(
    gsis_id: str = Path(..., description="Player GSIS ID"),
    season: int = Path(..., description="NFL season year", ge=2020, le=2030),
    week: int = Path(..., description="Week number", ge=1, le=22),
    league_key: str = Query(..., description="League key for scoring rules"),
    db: AsyncSession = Depends(get_db)
) -> FantasyPointsResponse:
    """
    Calculate fantasy points for a specific player.
    
    Args:
        gsis_id: Player GSIS ID
        season: NFL season year
        week: Week number
        league_key: League key for scoring rules
        
    Returns:
        Player's calculated fantasy points and breakdown
    """
    try:
        calculator = FantasyPointsCalculator(db)
        result = await calculator.calculate_player_points(gsis_id, season, week, league_key)
        
        return FantasyPointsResponse(
            gsis_id=result["gsis_id"],
            season=result["season"],
            week=result["week"],
            fantasy_points=result["fantasy_points"],
            scoring_breakdown=result["scoring_breakdown"],
            scoring_system=ScoringSystem(**result["scoring_system"])
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate fantasy points: {str(e)}"
        )


@router.get("/points/team/{team_key}/{season}/{week}")
async def calculate_team_fantasy_points(
    team_key: str = Path(..., description="Team key"),
    season: int = Path(..., description="NFL season year", ge=2020, le=2030),
    week: int = Path(..., description="Week number", ge=1, le=22),
    league_key: str = Query(..., description="League key for scoring rules"),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Calculate total fantasy points for a team's lineup.
    
    Args:
        team_key: Team key
        season: NFL season year
        week: Week number
        league_key: League key for scoring rules
        
    Returns:
        Team's total fantasy points and player breakdowns
    """
    try:
        calculator = FantasyPointsCalculator(db)
        result = await calculator.calculate_team_points(team_key, season, week, league_key)
        
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate team fantasy points: {str(e)}"
        )


@router.post("/parse/yahoo")
async def parse_yahoo_scoring_rules(
    scoring_json: str,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Parse Yahoo scoring rules and return the scoring system.
    
    Args:
        scoring_json: JSON string containing Yahoo scoring rules
        
    Returns:
        Parsed scoring system
    """
    try:
        scoring_engine = ScoringEngine.from_yahoo_scoring(scoring_json)
        scoring_system = scoring_engine.get_scoring_system()
        
        return {
            "success": True,
            "scoring_system": scoring_system.dict(),
            "rules_count": len(scoring_engine.scoring_rules)
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse scoring rules: {str(e)}"
        )


@router.get("/system/{league_key}")
async def get_league_scoring_system(
    league_key: str = Path(..., description="League key"),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get the scoring system for a specific league.
    
    Args:
        league_key: League key
        
    Returns:
        League's scoring system
    """
    try:
        from app.models.fantasy import League
        from sqlalchemy import select
        
        # Get league scoring rules
        league_result = await db.execute(
            select(League).where(League.league_key == league_key)
        )
        league = league_result.scalar_one_or_none()
        
        if not league:
            raise HTTPException(
                status_code=404,
                detail=f"League {league_key} not found"
            )
        
        if not league.scoring_json:
            raise HTTPException(
                status_code=404,
                detail=f"No scoring rules found for league {league_key}"
            )
        
        # Parse scoring rules
        scoring_engine = ScoringEngine.from_yahoo_scoring(league.scoring_json)
        scoring_system = scoring_engine.get_scoring_system()
        
        return {
            "league_key": league_key,
            "league_name": league.name,
            "scoring_system": scoring_system.dict(),
            "rules_count": len(scoring_engine.scoring_rules)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get scoring system: {str(e)}"
        )


@router.post("/test/calculate")
async def test_fantasy_calculation(
    stats: Dict[str, Any],
    scoring_json: str,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Test fantasy point calculation with custom stats and scoring rules.
    
    Args:
        stats: Dictionary of player statistics
        scoring_json: JSON string containing scoring rules
        
    Returns:
        Calculated fantasy points and breakdown
    """
    try:
        scoring_engine = ScoringEngine.from_yahoo_scoring(scoring_json)
        total_points, breakdown = scoring_engine.calculate_fantasy_points(stats)
        
        return {
            "success": True,
            "total_fantasy_points": total_points,
            "scoring_breakdown": breakdown,
            "scoring_system": scoring_engine.get_scoring_system().dict()
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate fantasy points: {str(e)}"
        )
