"""
Tests for Pydantic schemas.
"""

import pytest
from datetime import datetime, timezone
from pydantic import ValidationError

from app.schemas.auth import (
    OAuthStartRequest, OAuthStartResponse, OAuthCallbackRequest, 
    OAuthCallbackResponse, TokenInfo, UserInfo, AuthError
)
from app.schemas.yahoo import (
    LeagueInfo, TeamInfo, PlayerInfo, RosterSlot, TeamRoster,
    LeaguePlayerStatus, DraftPickInfo, LeagueSyncRequest, 
    LeagueSyncResponse, UserLeaguesResponse, SyncError
)


class TestAuthSchemas:
    """Test authentication schemas."""
    
    def test_oauth_start_request(self):
        """Test OAuth start request schema."""
        request = OAuthStartRequest()
        
        assert request.redirect_after_auth is None
    
    def test_oauth_start_request_with_params(self):
        """Test OAuth start request schema with parameters."""
        request = OAuthStartRequest(
            redirect_after_auth="http://localhost:8000/callback"
        )
        
        assert request.redirect_after_auth == "http://localhost:8000/callback"
    
    def test_oauth_start_response(self):
        """Test OAuth start response schema."""
        response = OAuthStartResponse(
            authorization_url="https://api.login.yahoo.com/oauth2/request_auth?client_id=test",
            state="test-state-123"
        )
        
        assert response.authorization_url == "https://api.login.yahoo.com/oauth2/request_auth?client_id=test"
        assert response.state == "test-state-123"
    
    def test_oauth_callback_request(self):
        """Test OAuth callback request schema."""
        request = OAuthCallbackRequest(
            code="test-code-123",
            state="test-state-123"
        )
        
        assert request.code == "test-code-123"
        assert request.state == "test-state-123"
    
    def test_oauth_callback_request_error(self):
        """Test OAuth callback request schema with error."""
        request = OAuthCallbackRequest(
            code="test-code-123",
            state="test-state-123"
        )
        
        assert request.code == "test-code-123"
        assert request.state == "test-state-123"
    
    def test_oauth_callback_response_success(self):
        """Test OAuth callback response schema for success."""
        from datetime import datetime, timezone
        
        user_info = UserInfo(
            id="test-user-123",
            email="test@example.com",
            username="testuser",
            display_name="Test User",
            created_at=datetime.now(timezone.utc)
        )
        
        token_info = TokenInfo(
            access_token="test-access-token",
            refresh_token="test-refresh-token",
            expires_at=datetime.now(timezone.utc),
            token_type="Bearer",
            scope="read"
        )
        
        response = OAuthCallbackResponse(
            success=True,
            user_id="test-user-123",
            message="Authentication successful"
        )
        
        assert response.success is True
        assert response.user_id == "test-user-123"
        assert response.message == "Authentication successful"
    
    def test_oauth_callback_response_error(self):
        """Test OAuth callback response schema for error."""
        response = OAuthCallbackResponse(
            success=False,
            message="Authentication failed"
        )
        
        assert response.success is False
        assert response.user_id is None
        assert response.message == "Authentication failed"
    
    def test_token_info(self):
        """Test token info schema."""
        token_info = TokenInfo(
            access_token="test-access-token",
            refresh_token="test-refresh-token",
            expires_at=datetime.now(timezone.utc),
            token_type="Bearer",
            scope="read"
        )
        
        assert token_info.access_token == "test-access-token"
        assert token_info.refresh_token == "test-refresh-token"
        assert token_info.token_type == "Bearer"
        assert token_info.scope == "read"
        assert isinstance(token_info.expires_at, datetime)
    
    def test_user_info(self):
        """Test user info schema."""
        from datetime import datetime, timezone
        
        user_info = UserInfo(
            id="test-user-123",
            email="test@example.com",
            username="testuser",
            display_name="Test User",
            created_at=datetime.now(timezone.utc)
        )
        
        assert user_info.id == "test-user-123"
        assert user_info.email == "test@example.com"
        assert user_info.username == "testuser"
        assert user_info.display_name == "Test User"
    
    def test_auth_error(self):
        """Test auth error schema."""
        error = AuthError(
            error="invalid_grant",
            error_description="Invalid authorization code"
        )
        
        assert error.error == "invalid_grant"
        assert error.error_description == "Invalid authorization code"


class TestYahooSchemas:
    """Test Yahoo API schemas."""
    
    def test_league_info(self):
        """Test league info schema."""
        league = LeagueInfo(
            league_key="414.l.123456",
            name="Test League",
            season=2024,
            league_type="standard",
            num_teams=12,
            is_finished=False
        )
        
        assert league.league_key == "414.l.123456"
        assert league.name == "Test League"
        assert league.season == 2024
        assert league.league_type == "standard"
        assert league.num_teams == 12
        assert league.is_finished is False
    
    def test_team_info(self):
        """Test team info schema."""
        team = TeamInfo(
            team_key="414.l.123456.t.1",
            name="Test Team",
            manager="Test Manager",
            division_id=1,
            rank=1,
            wins=8,
            losses=4,
            ties=0
        )
        
        assert team.team_key == "414.l.123456.t.1"
        assert team.name == "Test Team"
        assert team.manager == "Test Manager"
        assert team.division_id == 1
        assert team.rank == 1
        assert team.wins == 8
        assert team.losses == 4
        assert team.ties == 0
    
    def test_player_info(self):
        """Test player info schema."""
        player = PlayerInfo(
            player_id_yahoo="414.p.12345",
            full_name="Test Player",
            first_name="Test",
            last_name="Player",
            position="QB",
            team="TEST",
            bye_week=8,
            is_active=True
        )
        
        assert player.player_id_yahoo == "414.p.12345"
        assert player.full_name == "Test Player"
        assert player.first_name == "Test"
        assert player.last_name == "Player"
        assert player.position == "QB"
        assert player.team == "TEST"
        assert player.bye_week == 8
        assert player.is_active is True
    
    def test_roster_slot(self):
        """Test roster slot schema."""
        slot = RosterSlot(
            slot="QB",
            player_id_yahoo="414.p.12345",
            is_starting=True
        )
        
        assert slot.slot == "QB"
        assert slot.player_id_yahoo == "414.p.12345"
        assert slot.is_starting is True
    
    def test_roster_slot_empty(self):
        """Test roster slot schema with no player."""
        slot = RosterSlot(
            slot="QB",
            player_id_yahoo=None,
            is_starting=False
        )
        
        assert slot.slot == "QB"
        assert slot.player_id_yahoo is None
        assert slot.is_starting is False
    
    def test_team_roster(self):
        """Test team roster schema."""
        roster_slots = [
            RosterSlot(slot="QB", player_id_yahoo="414.p.12345", is_starting=True),
            RosterSlot(slot="RB", player_id_yahoo="414.p.12346", is_starting=True),
            RosterSlot(slot="WR", player_id_yahoo="414.p.12347", is_starting=True),
            RosterSlot(slot="TE", player_id_yahoo="414.p.12348", is_starting=True),
            RosterSlot(slot="FLEX", player_id_yahoo="414.p.12349", is_starting=True),
            RosterSlot(slot="K", player_id_yahoo="414.p.12350", is_starting=True),
            RosterSlot(slot="DEF", player_id_yahoo="414.p.12351", is_starting=True)
        ]
        
        roster = TeamRoster(
            team_key="414.l.123456.t.1",
            week=1,
            slots=roster_slots
        )
        
        assert roster.team_key == "414.l.123456.t.1"
        assert roster.week == 1
        assert len(roster.slots) == 7
        assert roster.slots[0].slot == "QB"
        assert roster.slots[0].is_starting is True
    
    def test_league_player_status(self):
        """Test league player status schema."""
        player_status = LeaguePlayerStatus(
            player_id_yahoo="414.p.12345",
            status="FA",
            percent_rostered=45,
            faab_cost_est=5,
            owner_team_key=None
        )
        
        assert player_status.player_id_yahoo == "414.p.12345"
        assert player_status.status == "FA"
        assert player_status.percent_rostered == 45
        assert player_status.faab_cost_est == 5
        assert player_status.owner_team_key is None
    
    def test_draft_pick_info(self):
        """Test draft pick info schema."""
        draft_pick = DraftPickInfo(
            round=1,
            pick=1,
            team_key="414.l.123456.t.1",
            player_id_yahoo="414.p.12345",
            cost=50
        )
        
        assert draft_pick.round == 1
        assert draft_pick.pick == 1
        assert draft_pick.team_key == "414.l.123456.t.1"
        assert draft_pick.player_id_yahoo == "414.p.12345"
        assert draft_pick.cost == 50
    
    def test_league_sync_request(self):
        """Test league sync request schema."""
        request = LeagueSyncRequest(
            include_teams=True,
            include_players=True,
            include_draft=False,
            include_transactions=True
        )
        
        assert request.include_teams is True
        assert request.include_players is True
        assert request.include_draft is False
        assert request.include_transactions is True
    
    def test_league_sync_request_defaults(self):
        """Test league sync request schema with defaults."""
        request = LeagueSyncRequest()
        
        assert request.include_teams is True
        assert request.include_players is True
        assert request.include_draft is True
        assert request.include_transactions is False
    
    def test_league_sync_response(self):
        """Test league sync response schema."""
        response = LeagueSyncResponse(
            success=True,
            league_key="414.l.123456",
            message="League synced successfully",
            teams_synced=12,
            players_synced=180,
            draft_picks_synced=144
        )
        
        assert response.success is True
        assert response.league_key == "414.l.123456"
        assert response.message == "League synced successfully"
        assert response.teams_synced == 12
        assert response.players_synced == 180
        assert response.draft_picks_synced == 144
    
    def test_league_sync_response_error(self):
        """Test league sync response schema with error."""
        response = LeagueSyncResponse(
            success=False,
            league_key="414.l.123456",
            message="Sync failed"
        )
        
        assert response.success is False
        assert response.league_key == "414.l.123456"
        assert response.message == "Sync failed"
        assert response.teams_synced is None
        assert response.players_synced is None
        assert response.draft_picks_synced is None
    
    def test_user_leagues_response(self):
        """Test user leagues response schema."""
        leagues = [
            LeagueInfo(
                league_key="414.l.123456",
                name="Test League 1",
                season=2024,
                league_type="standard",
                num_teams=12,
                is_finished=False
            ),
            LeagueInfo(
                league_key="414.l.123457",
                name="Test League 2",
                season=2024,
                league_type="ppr",
                num_teams=10,
                is_finished=False
            )
        ]
        
        response = UserLeaguesResponse(
            leagues=leagues,
            total_count=2
        )
        
        assert len(response.leagues) == 2
        assert response.total_count == 2
        assert response.leagues[0].name == "Test League 1"
        assert response.leagues[1].name == "Test League 2"
    
    def test_sync_error(self):
        """Test sync error schema."""
        error = SyncError(
            error="validation_error",
            error_description="Invalid league key format"
        )
        
        assert error.error == "validation_error"
        assert error.error_description == "Invalid league key format"
    
    def test_schema_validation_errors(self):
        """Test schema validation with invalid data."""
        # Test missing required field
        with pytest.raises(ValidationError):
            LeagueInfo(
                name="Test League",
                season=2024,
                league_type="standard",
                num_teams=12,
                is_finished=False
            )
        
        # Test missing required field
        with pytest.raises(ValidationError):
            TeamInfo(
                name="Test Team",
                manager="Test Manager",
                division_id=1,
                rank=1,
                wins=8,
                losses=4,
                ties=0
            )
        
        # Test missing required field
        with pytest.raises(ValidationError):
            PlayerInfo(
                full_name="Test Player",
                first_name="Test",
                last_name="Player",
                position="QB",
                team="TEST",
                bye_week=8,
                is_active=True
            )
        
        # Test missing required field
        with pytest.raises(ValidationError):
            PlayerInfo(
                player_id_yahoo="414.p.12345",
                full_name="Test Player",
                first_name="Test",
                last_name="Player",
                team="TEST",
                bye_week=8,
                is_active=True
            )

