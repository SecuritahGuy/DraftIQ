"""
Tests for API endpoints.
"""

import pytest
from httpx import AsyncClient
from unittest.mock import patch, MagicMock
import json

from app.models.user import User, YahooToken
from app.models.fantasy import League, Team, Player


class TestAuthEndpoints:
    """Test authentication endpoints."""
    
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_auth_status_not_authenticated(self, client: AsyncClient):
        """Test auth status when not authenticated."""
        response = await client.get("/api/v1/auth/status")
        
        assert response.status_code == 200
        data = response.json()
        assert data["authenticated"] is False
        assert "message" in data
    
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_start_yahoo_oauth(self, client: AsyncClient):
        """Test starting Yahoo OAuth flow."""
        response = await client.post("/api/v1/auth/yahoo/start", json={})
        
        assert response.status_code == 200
        data = response.json()
        assert "authorization_url" in data
        assert "state" in data
        assert "https://api.login.yahoo.com/oauth2/request_auth" in data["authorization_url"]
    
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_yahoo_oauth_authorize(self, client: AsyncClient):
        """Test Yahoo OAuth authorize redirect."""
        response = await client.get("/api/v1/auth/yahoo/authorize")
        
        # Should redirect to Yahoo
        assert response.status_code == 307
        assert "api.login.yahoo.com" in response.headers.get("location", "")
    
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_yahoo_oauth_callback_success(self, client: AsyncClient, db_session):
        """Test successful OAuth callback."""
        # Create a user first
        user = User(
            id="test-user-123",
            email="test@example.com",
            username="testuser",
            is_active=True,
            is_verified=True,
            display_name="Test User"
        )
        db_session.add(user)
        await db_session.commit()
        
        # Mock successful token exchange
        mock_token_response = {
            "access_token": "test-access-token",
            "refresh_token": "test-refresh-token",
            "expires_in": 3600,
            "token_type": "Bearer",
            "scope": "read"
        }
        
        # Mock the OAuth state and Yahoo API calls
        with patch("app.api.v1.auth.oauth_states", {"test-state": {"user_id": "test-user-123"}}), \
             patch("httpx.AsyncClient.post") as mock_post:
            
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_token_response
            mock_post.return_value = mock_response
            
            response = await client.get(
                "/api/v1/auth/yahoo/callback",
                params={"code": "test-code", "state": "test-state"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "user_id" in data
    
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_yahoo_oauth_callback_error(self, client: AsyncClient):
        """Test OAuth callback with error."""
        # Mock the OAuth state and Yahoo API error response
        with patch("app.api.v1.auth.oauth_states", {"test-state": {"user_id": "test-user-123"}}), \
             patch("httpx.AsyncClient.post") as mock_post:
            
            # Mock Yahoo API error response
            mock_response = MagicMock()
            mock_response.status_code = 400
            mock_response.json.return_value = {
                "error": "invalid_grant",
                "error_description": "Invalid authorization code"
            }
            mock_post.return_value = mock_response
            
            response = await client.get(
                "/api/v1/auth/yahoo/callback",
                params={"code": "invalid-code", "state": "test-state"}
            )
            
            assert response.status_code == 400
            data = response.json()
            assert "detail" in data
            assert "OAuth callback failed" in data["detail"]


class TestYahooEndpoints:
    """Test Yahoo API endpoints."""
    
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_get_user_leagues(self, client: AsyncClient):
        """Test getting user leagues."""
        response = await client.get("/api/v1/yahoo/leagues")
        
        assert response.status_code == 200
        data = response.json()
        assert "leagues" in data
        assert isinstance(data["leagues"], list)
    
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_get_league_teams(self, client: AsyncClient):
        """Test getting league teams."""
        response = await client.get("/api/v1/yahoo/league/414.l.123456/teams")
        
        assert response.status_code == 200
        data = response.json()
        assert "teams" in data
        assert isinstance(data["teams"], list)
    
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_get_team_roster(self, client: AsyncClient):
        """Test getting team roster."""
        response = await client.get("/api/v1/yahoo/team/414.l.123456.t.1/roster")
        
        assert response.status_code == 200
        data = response.json()
        assert "slots" in data
        assert "team_key" in data
        assert data["team_key"] == "414.l.123456.t.1"
    
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_get_team_roster_with_week(self, client: AsyncClient):
        """Test getting team roster for specific week."""
        response = await client.get(
            "/api/v1/yahoo/team/414.l.123456.t.1/roster",
            params={"week": 5}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "slots" in data
        assert "week" in data
        assert data["week"] == 5
    
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_get_league_players(self, client: AsyncClient):
        """Test getting league players."""
        response = await client.get("/api/v1/yahoo/league/414.l.123456/players")
        
        assert response.status_code == 200
        data = response.json()
        assert "players" in data
        assert isinstance(data["players"], list)
    
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_get_draft_results(self, client: AsyncClient):
        """Test getting draft results."""
        response = await client.get("/api/v1/yahoo/league/414.l.123456/draft")
        
        assert response.status_code == 200
        data = response.json()
        assert "draft_picks" in data
        assert isinstance(data["draft_picks"], list)
    
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_sync_league_data(self, client: AsyncClient):
        """Test syncing league data."""
        response = await client.post("/api/v1/yahoo/league/414.l.123456/pull")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["league_key"] == "414.l.123456"
        assert "teams_synced" in data
        assert "players_synced" in data
        assert "draft_picks_synced" in data
    
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_sync_league_data_with_request(self, client: AsyncClient):
        """Test syncing league data with request body."""
        request_data = {
            "include_teams": True,
            "include_players": True,
            "include_draft": False,
            "include_transactions": True
        }
        
        response = await client.post(
            "/api/v1/yahoo/league/414.l.123456/pull",
            json=request_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["league_key"] == "414.l.123456"


class TestDataSyncEndpoints:
    """Test data synchronization endpoints."""
    
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_sync_league_data_endpoint(self, client: AsyncClient):
        """Test data sync league endpoint."""
        response = await client.post("/api/v1/data/sync/league/414.l.123456")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["league_key"] == "414.l.123456"
        assert "message" in data
    
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_import_nfl_data_ids(self, client: AsyncClient):
        """Test importing NFL data IDs."""
        # Mock nfl_data_py import
        mock_ids_df = MagicMock()
        mock_ids_df.iterrows.return_value = [
            (0, {
                "gsis_id": "00-0012345",
                "pfr_id": "P123456",
                "espn_id": "12345",
                "display_name": "Test Player",
                "first_name": "Test",
                "last_name": "Player",
                "position": "QB",
                "team_abbr": "TEST"
            })
        ]
        
        with patch("nfl_data_py.import_ids", return_value=mock_ids_df):
            response = await client.post("/api/v1/data/mapping/import-nfl-ids")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "mappings_created" in data
            assert "total_processed" in data
    
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_import_nfl_data_ids_not_installed(self, client: AsyncClient):
        """Test importing NFL data IDs when not installed."""
        # Mock the import statement inside the service method
        with patch("app.services.player_mapping.PlayerMappingService.import_nfl_data_ids") as mock_method:
            mock_method.return_value = {
                "success": False,
                "error": "nfl_data_py not installed. Install with: pip install nfl_data_py"
            }
            response = await client.post("/api/v1/data/mapping/import-nfl-ids")
            
            assert response.status_code == 500
            data = response.json()
            assert "nfl_data_py not installed" in data["detail"]
    
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_map_yahoo_to_gsis_found(self, client: AsyncClient, db_session):
        """Test mapping Yahoo to GSIS ID when found."""
        from app.models.nfl_data import PlayerIDMapping
        
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
        
        response = await client.get("/api/v1/data/mapping/yahoo-to-gsis/414.p.12345")
        
        assert response.status_code == 200
        data = response.json()
        assert data["yahoo_player_id"] == "414.p.12345"
        assert data["gsis_id"] == "00-0012345"
        assert data["mapped"] is True
    
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_map_yahoo_to_gsis_not_found(self, client: AsyncClient):
        """Test mapping Yahoo to GSIS ID when not found."""
        response = await client.get("/api/v1/data/mapping/yahoo-to-gsis/414.p.99999")
        
        assert response.status_code == 200
        data = response.json()
        assert data["yahoo_player_id"] == "414.p.99999"
        assert data["gsis_id"] is None
        assert data["mapped"] is False
    
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_map_gsis_to_yahoo_found(self, client: AsyncClient, db_session):
        """Test mapping GSIS to Yahoo ID when found."""
        from app.models.nfl_data import PlayerIDMapping
        
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
        
        response = await client.get("/api/v1/data/mapping/gsis-to-yahoo/00-0012345")
        
        assert response.status_code == 200
        data = response.json()
        assert data["gsis_id"] == "00-0012345"
        assert data["yahoo_player_id"] == "414.p.12345"
        assert data["mapped"] is True
    
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_map_gsis_to_yahoo_not_found(self, client: AsyncClient):
        """Test mapping GSIS to Yahoo ID when not found."""
        response = await client.get("/api/v1/data/mapping/gsis-to-yahoo/00-0099999")
        
        assert response.status_code == 200
        data = response.json()
        assert data["gsis_id"] == "00-0099999"
        assert data["yahoo_player_id"] is None
        assert data["mapped"] is False
    
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_search_player_mappings(self, client: AsyncClient, db_session):
        """Test searching player mappings."""
        from app.models.nfl_data import PlayerIDMapping
        
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
        
        response = await client.get(
            "/api/v1/data/mapping/search",
            params={"full_name": "Test Player"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "Test Player"
        assert "mappings" in data
        assert "count" in data
        assert data["count"] == 1
    
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_search_player_mappings_with_position(self, client: AsyncClient, db_session):
        """Test searching player mappings with position filter."""
        from app.models.nfl_data import PlayerIDMapping
        
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
        
        response = await client.get(
            "/api/v1/data/mapping/search",
            params={"full_name": "Test Player", "position": "QB"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "Test Player"
        assert data["position"] == "QB"
        assert data["count"] == 1
    
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_get_unmapped_yahoo_players(self, client: AsyncClient, db_session):
        """Test getting unmapped Yahoo players."""
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
        
        response = await client.get("/api/v1/data/mapping/unmapped-yahoo-players")
        
        assert response.status_code == 200
        data = response.json()
        assert "unmapped_players" in data
        assert "count" in data
        assert data["count"] == 1
        assert data["unmapped_players"][0]["player_id_yahoo"] == "414.p.12346"
    
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_suggest_mappings(self, client: AsyncClient, db_session):
        """Test suggesting mappings for a player."""
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
        await db_session.commit()
        
        response = await client.get("/api/v1/data/mapping/suggest/414.p.12345")
        
        assert response.status_code == 200
        data = response.json()
        assert "yahoo_player" in data
        assert "suggestions" in data
        assert "count" in data
        assert data["yahoo_player"]["player_id_yahoo"] == "414.p.12345"
    
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_suggest_mappings_player_not_found(self, client: AsyncClient):
        """Test suggesting mappings for non-existent player."""
        response = await client.get("/api/v1/data/mapping/suggest/414.p.99999")
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]
    
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_get_cached_league_data_no_cache(self, client: AsyncClient):
        """Test getting cached league data when no cache exists."""
        response = await client.get("/api/v1/data/cache/league/414.l.123456")
        
        assert response.status_code == 200
        data = response.json()
        assert data["cached"] is False
        assert data["league_key"] == "414.l.123456"
        assert "No recent cached data found" in data["message"]
    
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_get_cached_league_data_with_cache(self, client: AsyncClient, db_session):
        """Test getting cached league data when cache exists."""
        # Create league with recent update
        from datetime import datetime, timezone
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
        
        response = await client.get("/api/v1/data/cache/league/414.l.123456")
        
        assert response.status_code == 200
        data = response.json()
        assert data["cached"] is True
        assert data["league_key"] == "414.l.123456"
        assert "data" in data
        assert "league" in data["data"]


class TestHealthEndpoints:
    """Test health check endpoints."""
    
    @pytest.mark.asyncio
    async def test_health_check(self, client: AsyncClient):
        """Test health check endpoint."""
        response = await client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_root_endpoint(self, client: AsyncClient):
        """Test root endpoint."""
        response = await client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "DraftIQ" in data["message"]
