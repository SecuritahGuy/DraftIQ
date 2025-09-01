"""
Player ID mapping service to bridge Yahoo player IDs with public NFL data sources.
"""

import asyncio
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import pandas as pd

from app.models.fantasy import Player
from app.models.nfl_data import PlayerIDMapping


class PlayerMappingService:
    """Service for mapping player IDs between different data sources."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def import_nfl_data_ids(self) -> Dict[str, Any]:
        """
        Import player IDs from nfl_data_py.
        
        This function uses nfl_data_py.import_ids() to get player ID mappings
        and stores them in our local database.
        
        Returns:
            Summary of import results
        """
        try:
            # Import nfl_data_py
            import nfl_data_py as nfl
            
            # Get player IDs from nfl_data_py
            ids_df = nfl.import_ids()
            
            # Process the data
            mappings_created = 0
            mappings_updated = 0
            
            for _, row in ids_df.iterrows():
                # Create or update mapping
                mapping = await self._create_or_update_mapping(row)
                if mapping:
                    mappings_created += 1
            
            return {
                "success": True,
                "mappings_created": mappings_created,
                "mappings_updated": mappings_updated,
                "total_processed": len(ids_df)
            }
            
        except ImportError:
            return {
                "success": False,
                "error": "nfl_data_py not installed. Install with: pip install nfl_data_py"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to import NFL data IDs: {str(e)}"
            }
    
    async def _create_or_update_mapping(self, row: pd.Series) -> Optional[PlayerIDMapping]:
        """
        Create or update a player ID mapping from nfl_data_py data.
        
        Args:
            row: Row from nfl_data_py import_ids() DataFrame
            
        Returns:
            PlayerIDMapping object or None if failed
        """
        try:
            # Extract data from row
            gsis_id = str(row.get('gsis_id', ''))
            pfr_id = str(row.get('pfr_id', '')) if pd.notna(row.get('pfr_id')) else None
            espn_id = str(row.get('espn_id', '')) if pd.notna(row.get('espn_id')) else None
            full_name = str(row.get('full_name', ''))
            first_name = str(row.get('first_name', '')) if pd.notna(row.get('first_name')) else None
            last_name = str(row.get('last_name', '')) if pd.notna(row.get('last_name')) else None
            position = str(row.get('position', ''))
            team = str(row.get('team', '')) if pd.notna(row.get('team')) else None
            
            if not gsis_id or not full_name:
                return None
            
            # Check if mapping exists
            stmt = select(PlayerIDMapping).where(PlayerIDMapping.gsis_id == gsis_id)
            result = await self.db.execute(stmt)
            existing_mapping = result.scalar_one_or_none()
            
            if existing_mapping:
                # Update existing mapping
                existing_mapping.pfr_id = pfr_id
                existing_mapping.espn_id = espn_id
                existing_mapping.full_name = full_name
                existing_mapping.first_name = first_name
                existing_mapping.last_name = last_name
                existing_mapping.position = position
                existing_mapping.team = team
                existing_mapping.is_active = True
                
                await self.db.commit()
                await self.db.refresh(existing_mapping)
                return existing_mapping
            else:
                # Create new mapping
                mapping = PlayerIDMapping(
                    gsis_id=gsis_id,
                    pfr_id=pfr_id,
                    espn_id=espn_id,
                    full_name=full_name,
                    first_name=first_name,
                    last_name=last_name,
                    position=position,
                    team=team,
                    is_active=True
                )
                
                self.db.add(mapping)
                await self.db.commit()
                await self.db.refresh(mapping)
                return mapping
                
        except Exception as e:
            print(f"Error creating mapping for row {row}: {e}")
            return None
    
    async def map_yahoo_to_gsis(self, yahoo_player_id: str) -> Optional[str]:
        """
        Map Yahoo player ID to GSIS ID.
        
        Args:
            yahoo_player_id: Yahoo player ID
            
        Returns:
            GSIS ID if found, None otherwise
        """
        # First, get the Yahoo player
        stmt = select(Player).where(Player.player_id_yahoo == yahoo_player_id)
        result = await self.db.execute(stmt)
        yahoo_player = result.scalar_one_or_none()
        
        if not yahoo_player:
            return None
        
        # Try to find matching GSIS ID by name and position
        stmt = select(PlayerIDMapping).where(
            PlayerIDMapping.full_name == yahoo_player.full_name,
            PlayerIDMapping.position == yahoo_player.position,
            PlayerIDMapping.is_active == True
        )
        result = await self.db.execute(stmt)
        mapping = result.scalar_one_or_none()
        
        return mapping.gsis_id if mapping else None
    
    async def map_gsis_to_yahoo(self, gsis_id: str) -> Optional[str]:
        """
        Map GSIS ID to Yahoo player ID.
        
        Args:
            gsis_id: GSIS ID
            
        Returns:
            Yahoo player ID if found, None otherwise
        """
        # Get the GSIS mapping
        stmt = select(PlayerIDMapping).where(
            PlayerIDMapping.gsis_id == gsis_id,
            PlayerIDMapping.is_active == True
        )
        result = await self.db.execute(stmt)
        mapping = result.scalar_one_or_none()
        
        if not mapping:
            return None
        
        # Try to find matching Yahoo player by name and position
        stmt = select(Player).where(
            Player.full_name == mapping.full_name,
            Player.position == mapping.position,
            Player.is_active == True
        )
        result = await self.db.execute(stmt)
        yahoo_player = result.scalar_one_or_none()
        
        return yahoo_player.player_id_yahoo if yahoo_player else None
    
    async def find_player_by_name(self, full_name: str, position: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Find player mappings by name.
        
        Args:
            full_name: Player's full name
            position: Player position (optional filter)
            
        Returns:
            List of player mappings
        """
        stmt = select(PlayerIDMapping).where(
            PlayerIDMapping.full_name == full_name,
            PlayerIDMapping.is_active == True
        )
        
        if position:
            stmt = stmt.where(PlayerIDMapping.position == position)
        
        result = await self.db.execute(stmt)
        mappings = result.scalars().all()
        
        return [
            {
                "gsis_id": mapping.gsis_id,
                "pfr_id": mapping.pfr_id,
                "espn_id": mapping.espn_id,
                "full_name": mapping.full_name,
                "position": mapping.position,
                "team": mapping.team
            }
            for mapping in mappings
        ]
    
    async def get_unmapped_yahoo_players(self) -> List[Player]:
        """
        Get Yahoo players that don't have GSIS ID mappings.
        
        Returns:
            List of unmapped Yahoo players
        """
        # Get Yahoo players that don't have GSIS ID
        stmt = select(Player).where(
            Player.is_active == True,
            Player.gsis_id.is_(None)
        )
        result = await self.db.execute(stmt)
        unmapped_players = result.scalars().all()
        
        return unmapped_players
    
    async def suggest_mappings(self, yahoo_player: Player) -> List[Dict[str, Any]]:
        """
        Suggest potential mappings for a Yahoo player.
        
        Args:
            yahoo_player: Yahoo player to find mappings for
            
        Returns:
            List of potential mappings with confidence scores
        """
        # Search for similar names in our mapping table
        stmt = select(PlayerIDMapping).where(
            PlayerIDMapping.is_active == True
        )
        result = await self.db.execute(stmt)
        all_mappings = result.scalars().all()
        
        suggestions = []
        for mapping in all_mappings:
            # Calculate similarity score
            name_similarity = self._calculate_name_similarity(
                yahoo_player.full_name, 
                mapping.full_name
            )
            
            position_match = yahoo_player.position == mapping.position
            
            # Only include if there's some similarity
            if name_similarity > 0.5 or (name_similarity > 0.3 and position_match):
                confidence = name_similarity
                if position_match:
                    confidence += 0.2
                
                suggestions.append({
                    "gsis_id": mapping.gsis_id,
                    "pfr_id": mapping.pfr_id,
                    "full_name": mapping.full_name,
                    "position": mapping.position,
                    "team": mapping.team,
                    "confidence": min(confidence, 1.0),
                    "yahoo_player": yahoo_player
                })
        
        # Sort by confidence
        suggestions.sort(key=lambda x: x["confidence"], reverse=True)
        return suggestions[:5]  # Return top 5 suggestions
    
    def _calculate_name_similarity(self, name1: str, name2: str) -> float:
        """
        Calculate similarity between two names.
        
        Args:
            name1: First name
            name2: Second name
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        # Simple implementation - can be improved with more sophisticated algorithms
        name1_lower = name1.lower().replace(" ", "")
        name2_lower = name2.lower().replace(" ", "")
        
        if name1_lower == name2_lower:
            return 1.0
        
        # Check if one name contains the other
        if name1_lower in name2_lower or name2_lower in name1_lower:
            return 0.8
        
        # Check for common variations
        if name1_lower.replace(".", "") == name2_lower.replace(".", ""):
            return 0.9
        
        # Simple character-based similarity for partial matches
        # Count common characters
        common_chars = 0
        for char in name1_lower:
            if char in name2_lower:
                common_chars += 1
        
        # Calculate similarity based on common characters
        max_len = max(len(name1_lower), len(name2_lower))
        if max_len > 0:
            similarity = common_chars / max_len
            # Only return similarity if it's reasonably high
            if similarity > 0.6:
                return similarity
        
        return 0.0
