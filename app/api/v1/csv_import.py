"""
CSV import API endpoints for custom projections and data.
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import StreamingResponse
import io

from app.core.database import get_db
from app.services.csv_import import CSVImportService

router = APIRouter()


@router.post("/projections")
async def import_projections_csv(
    file: UploadFile = File(..., description="CSV file with projections"),
    source: str = Form(default="csv", description="Source identifier for projections"),
    season: int = Form(None, description="Override season (if not in CSV)"),
    week: int = Form(None, description="Override week (if not in CSV)"),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Import projections from CSV file.
    
    Expected CSV format:
    player_name,position,team,season,week,passing_yards,passing_tds,passing_ints,
    rushing_yards,rushing_tds,receiving_yards,receiving_tds,receptions,fumbles_lost,
    field_goals,field_goal_attempts,extra_points,extra_point_attempts,confidence
    
    Args:
        file: CSV file with projections
        source: Source identifier for projections
        season: Override season (if not in CSV)
        week: Override week (if not in CSV)
        
    Returns:
        Import results with counts and any errors
    """
    try:
        # Validate file type
        if not file.filename.endswith('.csv'):
            raise HTTPException(
                status_code=400,
                detail="File must be a CSV file"
            )
        
        # Read file content
        content = await file.read()
        csv_content = content.decode('utf-8')
        
        # Import projections
        service = CSVImportService(db)
        result = await service.import_projections_csv(csv_content, source, season, week)
        
        if result["success"]:
            return {
                "success": True,
                "message": f"Successfully imported {result['projections_created']} new projections and updated {result['projections_updated']} existing projections",
                "projections_created": result["projections_created"],
                "projections_updated": result["projections_updated"],
                "total_processed": result["total_processed"],
                "errors": result["errors"],
                "error_count": result["error_count"]
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=result["error"]
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to import CSV: {str(e)}"
        )


@router.post("/projections/text")
async def import_projections_csv_text(
    csv_content: str = Form(..., description="CSV content as text"),
    source: str = Form(default="csv", description="Source identifier for projections"),
    season: int = Form(None, description="Override season (if not in CSV)"),
    week: int = Form(None, description="Override week (if not in CSV)"),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Import projections from CSV text content.
    
    Args:
        csv_content: CSV content as text
        source: Source identifier for projections
        season: Override season (if not in CSV)
        week: Override week (if not in CSV)
        
    Returns:
        Import results with counts and any errors
    """
    try:
        service = CSVImportService(db)
        result = await service.import_projections_csv(csv_content, source, season, week)
        
        if result["success"]:
            return {
                "success": True,
                "message": f"Successfully imported {result['projections_created']} new projections and updated {result['projections_updated']} existing projections",
                "projections_created": result["projections_created"],
                "projections_updated": result["projections_updated"],
                "total_processed": result["total_processed"],
                "errors": result["errors"],
                "error_count": result["error_count"]
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=result["error"]
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to import CSV: {str(e)}"
        )


@router.get("/template/projections")
async def get_projections_csv_template() -> Dict[str, Any]:
    """
    Get CSV template for projections import.
    
    Returns:
        CSV template content and instructions
    """
    try:
        service = CSVImportService(None)  # No DB needed for template
        template = await service.get_csv_template()
        
        return {
            "success": True,
            "template": template,
            "instructions": {
                "required_columns": ["player_name", "position"],
                "optional_columns": [
                    "team", "season", "week", "passing_yards", "passing_tds", "passing_ints",
                    "rushing_yards", "rushing_tds", "receiving_yards", "receiving_tds",
                    "receptions", "fumbles_lost", "field_goals", "field_goal_attempts",
                    "extra_points", "extra_point_attempts", "confidence"
                ],
                "position_values": ["QB", "RB", "WR", "TE", "K", "DEF"],
                "confidence_range": "0.0 to 1.0",
                "notes": [
                    "Player names should match names in the player database",
                    "If season/week are not provided in CSV, they must be specified in the request",
                    "All numeric fields default to 0 if not provided",
                    "Confidence defaults to 0.5 if not provided"
                ]
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get template: {str(e)}"
        )


@router.post("/validate/projections")
async def validate_projections_csv(
    file: UploadFile = File(..., description="CSV file to validate"),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Validate CSV format before import.
    
    Args:
        file: CSV file to validate
        
    Returns:
        Validation results
    """
    try:
        # Validate file type
        if not file.filename.endswith('.csv'):
            raise HTTPException(
                status_code=400,
                detail="File must be a CSV file"
            )
        
        # Read file content
        content = await file.read()
        csv_content = content.decode('utf-8')
        
        # Validate format
        service = CSVImportService(db)
        result = await service.validate_csv_format(csv_content)
        
        return {
            "success": True,
            "valid": result["valid"],
            "row_count": result.get("row_count", 0),
            "columns": result.get("columns", []),
            "missing_columns": result.get("missing_columns", []),
            "validation_errors": result.get("validation_errors", []),
            "error": result.get("error")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to validate CSV: {str(e)}"
        )


@router.get("/export/projections")
async def export_projections_csv(
    season: int = Query(..., description="NFL season year", ge=2020, le=2030),
    week: int = Query(..., description="Week number", ge=1, le=22),
    source: str = Query("internal", description="Projection source to export"),
    db: AsyncSession = Depends(get_db)
) -> StreamingResponse:
    """
    Export projections to CSV format.
    
    Args:
        season: NFL season year
        week: Week number
        source: Projection source to export
        
    Returns:
        CSV file with projections
    """
    try:
        service = CSVImportService(db)
        csv_content = await service.export_projections_csv(season, week, source)
        
        # Create streaming response
        output = io.StringIO(csv_content)
        
        return StreamingResponse(
            io.BytesIO(csv_content.encode('utf-8')),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=projections_{season}_week_{week}_{source}.csv"
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to export CSV: {str(e)}"
        )


@router.get("/export/projections/text")
async def export_projections_csv_text(
    season: int = Query(..., description="NFL season year", ge=2020, le=2030),
    week: int = Query(..., description="Week number", ge=1, le=22),
    source: str = Query("internal", description="Projection source to export"),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Export projections to CSV text format.
    
    Args:
        season: NFL season year
        week: Week number
        source: Projection source to export
        
    Returns:
        CSV content as text
    """
    try:
        service = CSVImportService(db)
        csv_content = await service.export_projections_csv(season, week, source)
        
        return {
            "success": True,
            "csv_content": csv_content,
            "filename": f"projections_{season}_week_{week}_{source}.csv"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to export CSV: {str(e)}"
        )
