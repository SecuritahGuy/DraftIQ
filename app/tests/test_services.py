"""
Tests for service classes.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timezone, timedelta
import json

from app.services.yahoo_oauth import YahooOAuthService
from app.services.yahoo_api import YahooAPIClient, YahooAPIService
from app.services.data_sync import DataSyncService
from app.services.player_mapping import PlayerMappingService
from app.models.user import User, YahooToken
from app.models.fantasy import League, Team, Player, LeaguePlayer, Roster, DraftPick
from app.models.nfl_data import PlayerIDMapping


class TestYahooOAuthService:
    """Test Yahoo OAuth service."""
    
    def test_generate_state(self):
        """Test state generation."""
        service = YahooOAuthService()
        state1 = service.generate_state()
        state2 = service.generate_state()
        
        assert isinstance(state1, str)
        assert len(state1) > 10
        assert state1 != state2
    
    def test_get_authorization_url(self):
        """Test authorization URL generation."""
        service = YahooOAuthService()
        state = "test-state-123"
        auth_url = service.get_authorization_url(state)
        
        assert "https://api.login.yahoo.com/oauth2/request_auth" in auth_url
        assert "client_id=" in auth_url
        assert "redirect_uri=" in auth_url
        assert "response_type=code" in auth_url
        assert f"state={state}" in auth_url
        assert "scope=" in auth_url
    
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_parse_token_response(self):
        """Test token response parsing."""
        service = YahooOAuthService()
        
        # Test successful response
        response_data = {
            "access_token": "test-access-token",
            "refresh_token": "test-refresh-token",
            "expires_in": 3600,
            "token_type": "Bearer",
            "scope": "read"
        }
        
        result = service.parse_token_response(response_data)
        
        assert result["access_token"] == "test-access-token"
        assert result["refresh_token"] == "test-refresh-token"
        assert result["token_type"] == "Bearer"
        assert result["scope"] == "read"
        assert "expires_at" in result
        assert isinstance(result["expires_at"], datetime)
    
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_parse_token_response_error(self):
        """Test token response parsing with error."""
        service = YahooOAuthService()
        
        # Test error response
        response_data = {
            "error": "invalid_grant",
            "error_description": "Invalid authorization code"
        }
        
        with pytest.raises(Exception) as exc_info:
            service.parse_token_response(response_data)
        
        assert "Invalid authorization code" in str(exc_info.value)


class TestYahooAPIClient:
    """Test Yahoo API client."""
    
    def test_init(self):
        """Test client initialization."""
        access_token = "test-access-token"
        client = YahooAPIClient(access_token)
        
        assert client.access_token == access_token
        assert "fantasysports.yahooapis.com" in client.base_url
        assert client.headers["Authorization"] == f"Bearer {access_token}"
        assert client.headers["Content-Type"] == "application/json"
    
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_make_request_success(self):
        """Test successful API request."""
        client = YahooAPIClient("test-token")
        
        # Mock httpx response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"fantasy_content": {"users": []}}
        
        with patch("httpx.AsyncClient.get", return_value=mock_response):
            result = await client._make_request("test/endpoint")
            
            assert result == {"fantasy_content": {"users": []}}
    
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_make_request_error(self):
        """Test API request with error."""
        client = YahooAPIClient("test-token")
        
        # Mock httpx response with error
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = Exception("Unauthorized")
        
        with patch("httpx.AsyncClient.get", return_value=mock_response):
            with pytest.raises(Exception):
                await client._make_request("test/endpoint")
    
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_get_user_leagues(self):
        """Test getting user leagues."""
        client = YahooAPIClient("test-token")
        
        # Mock response data
        mock_response_data = {
            "fantasy_content": {
                "users": {
                    "0": {
                        "user": {
                            "games": {
                                "0": {
                                    "leagues": {
                                        "0": {
                                            "league": {
                                                "league_key": "414.l.123456",
                                                "name": "Test League",
                                                "season": "2024"
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        
        with patch.object(client, "_make_request", return_value=mock_response_data):
            leagues = await client.get_user_leagues()
            
            assert len(leagues) == 1
            assert leagues[0]["league_key"] == "414.l.123456"
            assert leagues[0]["name"] == "Test League"
            assert leagues[0]["season"] == "2024"


class TestDataSyncService:
    """Test data synchronization service."""
    
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_sync_league_data_new_league(self, db_session):
        """Test syncing new league data."""
        service = DataSyncService(db_session)
        
        league_data = {
            "league_key": "414.l.123456",
            "name": "Test League",
            "season": 2024,
            "scoring_json": '{"passing_yards": 0.04}',
            "roster_slots_json": '{"QB": 1}',
            "league_type": "standard",
            "num_teams": 12,
            "is_finished": False
        }
        
        league = await service.sync_league_data(league_data)
        
        assert league.league_key == "414.l.123456"
        assert league.name == "Test League"
        assert league.season == 2024
        
        # Verify it was saved to database
        from sqlalchemy import select
        stmt = select(League).where(League.league_key == "414.l.123456")
        result = await db_session.execute(stmt)
        saved_league = result.scalar_one_or_none()
        assert saved_league is not None
        assert saved_league.name == "Test League"
    
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_sync_league_data_update_existing(self, db_session):
        """Test updating existing league data."""
        service = DataSyncService(db_session)
        
        # Create initial league
        initial_league = League(
            league_key="414.l.123456",
            name="Old Name",
            season=2024,
            scoring_json='{"passing_yards": 0.04}',
            roster_slots_json='{"QB": 1}',
            league_type="standard",
            num_teams=12,
            is_finished=False
        )
        db_session.add(initial_league)
        await db_session.commit()
        
        # Update league data
        updated_data = {
            "league_key": "414.l.123456",
            "name": "Updated Name",
            "season": 2024,
            "league_type": "ppr",
            "num_teams": 14,
            "is_finished": True,
            "settings": {
                "scoring_settings": {"passing_yards": 0.05},
                "roster_positions": {"QB": 1, "RB": 2}
            }
        }
        
        league = await service.sync_league_data(updated_data)
        
        assert league.name == "Updated Name"
        assert league.scoring_json == '{"passing_yards": 0.05}'
        assert league.roster_slots_json == '{"QB": 1, "RB": 2}'
        assert league.league_type == "ppr"
        assert league.num_teams == 14
        assert league.is_finished is True
    
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_sync_teams_data(self, db_session):
        """Test syncing teams data."""
        service = DataSyncService(db_session)
        
        # Create league first
        league = League(
            league_key="414.l.123456",
            name="Test League",
            season=2024,
            scoring_json='{"passing_yards": 0.04}',
            roster_slots_json='{"QB": 1}',
            league_type="standard",
            num_teams=12,
            is_finished=False
        )
        db_session.add(league)
        await db_session.commit()
        
        teams_data = [
            {
                "team_key": "414.l.123456.t.1",
                "league_key": "414.l.123456",
                "name": "Team 1",
                "manager": "Manager 1",
                "division_id": 1,
                "rank": 1,
                "wins": 8,
                "losses": 4,
                "ties": 0
            },
            {
                "team_key": "414.l.123456.t.2",
                "league_key": "414.l.123456",
                "name": "Team 2",
                "manager": "Manager 2",
                "division_id": 1,
                "rank": 2,
                "wins": 7,
                "losses": 5,
                "ties": 0
            }
        ]
        
        teams = await service.sync_teams_data("414.l.123456", teams_data)
        
        assert len(teams) == 2
        assert teams[0].name == "Team 1"
        assert teams[1].name == "Team 2"
        
        # Verify teams were saved
        from sqlalchemy import select
        stmt = select(Team).where(Team.league_key == "414.l.123456")
        result = await db_session.execute(stmt)
        saved_teams = result.scalars().all()
        assert len(saved_teams) == 2
    
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_sync_players_data(self, db_session):
        """Test syncing players data."""
        service = DataSyncService(db_session)
        
        players_data = [
            {
                "player_id": "414.p.12345",
                "name": {
                    "full": "Test Player 1",
                    "first": "Test",
                    "last": "Player 1"
                },
                "display_position": "QB",
                "editorial_team_abbr": "TEST",
                "bye_weeks": {
                    "week": 8
                }
            },
            {
                "player_id": "414.p.12346",
                "name": {
                    "full": "Test Player 2",
                    "first": "Test",
                    "last": "Player 2"
                },
                "display_position": "RB",
                "editorial_team_abbr": "TEST",
                "bye_weeks": {
                    "week": 8
                }
            }
        ]
        
        players = await service.sync_players_data("414.l.123456", players_data)
        
        assert len(players) == 2
        assert players[0].full_name == "Test Player 1"
        assert players[1].full_name == "Test Player 2"
        
        # Verify players were saved
        from sqlalchemy import select
        stmt = select(Player).where(Player.is_active == True)
        result = await db_session.execute(stmt)
        saved_players = result.scalars().all()
        assert len(saved_players) == 2
    
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_get_cached_league_data_no_cache(self, db_session):
        """Test getting cached league data when no cache exists."""
        service = DataSyncService(db_session)
        
        cached_data = await service.get_cached_league_data("414.l.123456")
        
        assert cached_data is None
    
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_get_cached_league_data_with_cache(self, db_session):
        """Test getting cached league data when cache exists."""
        service = DataSyncService(db_session)
        
        # Create league with recent update
        league = League(
            league_key="414.l.123456",
            name="Test League",
            season=2024,
            scoring_json='{"passing_yards": 0.04}',
            roster_slots_json='{"QB": 1}',
            league_type="standard",
            num_teams=12,
            is_finished=False,
            updated_at=datetime.now(timezone.utc)
        )
        db_session.add(league)
        await db_session.commit()
        
        cached_data = await service.get_cached_league_data("414.l.123456", max_age_hours=24)
        
        assert cached_data is not None
        assert "league" in cached_data
        assert cached_data["league"].league_key == "414.l.123456"
        assert "teams" in cached_data
        assert "players" in cached_data


class TestPlayerMappingService:
    """Test player mapping service."""
    
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_import_nfl_data_ids_success(self, db_session):
        """Test successful NFL data import."""
        service = PlayerMappingService(db_session)
        
        # Mock nfl_data_py import
        mock_ids_df = MagicMock()
        mock_ids_df.iterrows.return_value = [
            (0, {
                "gsis_id": "00-0012345",
                "pfr_id": "P123456",
                "espn_id": "12345",
                "full_name": "Test Player",
                "first_name": "Test",
                "last_name": "Player",
                "position": "QB",
                "team": "TEST"
            })
        ]
        mock_ids_df.__len__ = MagicMock(return_value=1)
        
        with patch("nfl_data_py.import_ids", return_value=mock_ids_df):
            result = await service.import_nfl_data_ids()
            
            assert result["success"] is True
            assert result["mappings_created"] == 1
            assert result["total_processed"] == 1
    
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_import_nfl_data_ids_not_installed(self, db_session):
        """Test NFL data import when nfl_data_py is not installed."""
        service = PlayerMappingService(db_session)
        
        with patch("nfl_data_py.import_ids", side_effect=ImportError):
            result = await service.import_nfl_data_ids()
            
            assert result["success"] is False
            assert "nfl_data_py not installed" in result["error"]
    
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_map_yahoo_to_gsis_found(self, db_session):
        """Test mapping Yahoo to GSIS ID when mapping exists."""
        from app.models.nfl_data import PlayerIDMapping
        
        service = PlayerMappingService(db_session)
        
        # Create player
        player = Player(
            player_id_yahoo="414.p.12345",
            gsis_id="00-0012345",
            pfr_id="P123456",
            full_name="Test Player",
            first_name="Test",
            last_name="Player",
            position="QB",
            team="TEST",
            bye_week=8,
            is_active=True
        )
        db_session.add(player)
        
        # Create player ID mapping
        mapping = PlayerIDMapping(
            gsis_id="00-0012345",
            pfr_id="P123456",
            espn_id="12345",
            full_name="Test Player",
            first_name="Test",
            last_name="Player",
            position="QB",
            team="TEST",
            is_active=True,
            confidence=0.95
        )
        db_session.add(mapping)
        await db_session.commit()
        
        gsis_id = await service.map_yahoo_to_gsis("414.p.12345")
        
        assert gsis_id == "00-0012345"
    
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_map_yahoo_to_gsis_not_found(self, db_session):
        """Test mapping Yahoo to GSIS ID when mapping doesn't exist."""
        service = PlayerMappingService(db_session)
        
        gsis_id = await service.map_yahoo_to_gsis("414.p.99999")
        
        assert gsis_id is None
    
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_map_gsis_to_yahoo_found(self, db_session):
        """Test mapping GSIS to Yahoo ID when mapping exists."""
        from app.models.nfl_data import PlayerIDMapping
        
        service = PlayerMappingService(db_session)
        
        # Create player
        player = Player(
            player_id_yahoo="414.p.12345",
            gsis_id="00-0012345",
            pfr_id="P123456",
            full_name="Test Player",
            first_name="Test",
            last_name="Player",
            position="QB",
            team="TEST",
            bye_week=8,
            is_active=True
        )
        db_session.add(player)
        
        # Create player ID mapping
        mapping = PlayerIDMapping(
            gsis_id="00-0012345",
            pfr_id="P123456",
            espn_id="12345",
            full_name="Test Player",
            first_name="Test",
            last_name="Player",
            position="QB",
            team="TEST",
            is_active=True,
            confidence=0.95
        )
        db_session.add(mapping)
        await db_session.commit()
        
        yahoo_id = await service.map_gsis_to_yahoo("00-0012345")
        
        assert yahoo_id == "414.p.12345"
    
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_map_gsis_to_yahoo_not_found(self, db_session):
        """Test mapping GSIS to Yahoo ID when mapping doesn't exist."""
        service = PlayerMappingService(db_session)
        
        yahoo_id = await service.map_gsis_to_yahoo("00-0099999")
        
        assert yahoo_id is None
    
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_find_player_by_name(self, db_session):
        """Test finding player by name."""
        from app.models.nfl_data import PlayerIDMapping
        
        service = PlayerMappingService(db_session)
        
        # Create player ID mapping
        mapping = PlayerIDMapping(
            gsis_id="00-0012345",
            pfr_id="P123456",
            espn_id="12345",
            full_name="Test Player",
            first_name="Test",
            last_name="Player",
            position="QB",
            team="TEST",
            is_active=True,
            confidence=0.95
        )
        db_session.add(mapping)
        await db_session.commit()
        
        mappings = await service.find_player_by_name("Test Player")
        
        assert len(mappings) == 1
        assert mappings[0]["full_name"] == "Test Player"
    
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_find_player_by_name_with_position(self, db_session):
        """Test finding player by name and position."""
        from app.models.nfl_data import PlayerIDMapping
        
        service = PlayerMappingService(db_session)
        
        # Create player ID mappings
        qb_mapping = PlayerIDMapping(
            gsis_id="00-0012345",
            pfr_id="P123456",
            espn_id="12345",
            full_name="Test Player",
            first_name="Test",
            last_name="Player",
            position="QB",
            team="TEST",
            is_active=True,
            confidence=0.95
        )
        rb_mapping = PlayerIDMapping(
            gsis_id="00-0012346",
            pfr_id="P123457",
            espn_id="12346",
            full_name="Test Player",
            first_name="Test",
            last_name="Player",
            position="RB",
            team="TEST",
            is_active=True,
            confidence=0.95
        )
        db_session.add_all([qb_mapping, rb_mapping])
        await db_session.commit()
        
        # Search for QB only
        mappings = await service.find_player_by_name("Test Player", "QB")
        
        assert len(mappings) == 1
        assert mappings[0]["position"] == "QB"
    
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_get_unmapped_yahoo_players(self, db_session):
        """Test getting unmapped Yahoo players."""
        service = PlayerMappingService(db_session)
        
        # Create players - one with GSIS ID, one without
        mapped_player = Player(
            player_id_yahoo="414.p.12345",
            gsis_id="00-0012345",
            pfr_id="P123456",
            full_name="Mapped Player",
            first_name="Mapped",
            last_name="Player",
            position="QB",
            team="TEST",
            bye_week=8,
            is_active=True
        )
        unmapped_player = Player(
            player_id_yahoo="414.p.12346",
            gsis_id=None,
            pfr_id=None,
            full_name="Unmapped Player",
            first_name="Unmapped",
            last_name="Player",
            position="RB",
            team="TEST",
            bye_week=8,
            is_active=True
        )
        db_session.add_all([mapped_player, unmapped_player])
        await db_session.commit()
        
        unmapped_players = await service.get_unmapped_yahoo_players()
        
        assert len(unmapped_players) == 1
        assert unmapped_players[0].player_id_yahoo == "414.p.12346"
        assert unmapped_players[0].full_name == "Unmapped Player"
    
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_suggest_mappings(self, db_session):
        """Test suggesting mappings for a player."""
        service = PlayerMappingService(db_session)
        
        # Create Yahoo player
        yahoo_player = Player(
            player_id_yahoo="414.p.12345",
            gsis_id=None,
            pfr_id=None,
            full_name="Test Player",
            first_name="Test",
            last_name="Player",
            position="QB",
            team="TEST",
            bye_week=8,
            is_active=True
        )
        db_session.add(yahoo_player)
        
        # Create potential mapping
        mapping = PlayerIDMapping(
            gsis_id="00-0012345",
            pfr_id="P123456",
            espn_id="12345",
            full_name="Test Player",
            first_name="Test",
            last_name="Player",
            position="QB",
            team="TEST",
            is_active=True,
            confidence=0.95
        )
        db_session.add(mapping)
        await db_session.commit()
        
        suggestions = await service.suggest_mappings(yahoo_player)
        
        assert len(suggestions) == 1
        assert suggestions[0]["gsis_id"] == "00-0012345"
        assert suggestions[0]["confidence"] > 0.8
    
    def test_calculate_name_similarity(self):
        """Test name similarity calculation."""
        service = PlayerMappingService(None)  # db not needed for this test
        
        # Test exact match
        similarity = service._calculate_name_similarity("John Smith", "John Smith")
        assert similarity == 1.0
        
        # Test partial match
        similarity = service._calculate_name_similarity("John Smith", "Johnny Smith")
        assert 0.5 < similarity < 1.0
        
        # Test no match
        similarity = service._calculate_name_similarity("John Smith", "Jane Doe")
        assert similarity < 0.5
