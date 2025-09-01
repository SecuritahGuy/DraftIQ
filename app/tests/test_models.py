"""
Tests for SQLAlchemy models.
"""

import pytest
import pytest_asyncio
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User, YahooToken
from app.models.fantasy import League, Team, Player, LeaguePlayer, Roster, DraftPick
from app.models.nfl_data import WeeklyStats, WeeklyProjections, Injuries, DepthCharts, PlayerIDMapping, Recommendations


class TestUserModels:
    """Test user-related models."""
    
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_create_user(self, db_session: AsyncSession, sample_user_data):
        """Test creating a user."""
        user = User(**sample_user_data)
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        assert user.id == sample_user_data["id"]
        assert user.email == sample_user_data["email"]
        assert user.username == sample_user_data["username"]
        assert user.is_active is True
        assert user.is_verified is True
        assert user.display_name == sample_user_data["display_name"]
        assert user.created_at is not None
        assert user.updated_at is not None
    
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_create_yahoo_token(self, db_session: AsyncSession, sample_user_data, sample_yahoo_token_data):
        """Test creating a Yahoo token."""
        # Create user first
        user = User(**sample_user_data)
        db_session.add(user)
        await db_session.commit()
        
        # Create token
        token = YahooToken(**sample_yahoo_token_data)
        db_session.add(token)
        await db_session.commit()
        await db_session.refresh(token)
        
        assert token.id == sample_yahoo_token_data["id"]
        assert token.user_id == sample_yahoo_token_data["user_id"]
        assert token.access_token == sample_yahoo_token_data["access_token"]
        assert token.refresh_token == sample_yahoo_token_data["refresh_token"]
        assert token.token_type == sample_yahoo_token_data["token_type"]
        assert token.scope == sample_yahoo_token_data["scope"]
        assert token.yahoo_user_id == sample_yahoo_token_data["yahoo_user_id"]
        assert token.yahoo_guid == sample_yahoo_token_data["yahoo_guid"]
    
    @pytest.mark.asyncio
    async def test_user_token_relationship(self, db_session: AsyncSession, sample_user_data, sample_yahoo_token_data):
        """Test user-token relationship."""
        from sqlalchemy.orm import selectinload
        from sqlalchemy import select
        
        # Create user
        user = User(**sample_user_data)
        db_session.add(user)
        await db_session.commit()
        
        # Create token
        token = YahooToken(**sample_yahoo_token_data)
        db_session.add(token)
        await db_session.commit()
        
        # Test relationship by querying with selectinload
        stmt = select(User).options(selectinload(User.yahoo_tokens)).where(User.id == user.id)
        result = await db_session.execute(stmt)
        user_with_tokens = result.scalar_one()
        
        assert len(user_with_tokens.yahoo_tokens) == 1
        assert user_with_tokens.yahoo_tokens[0].id == token.id


class TestFantasyModels:
    """Test fantasy football models."""
    
    @pytest.mark.asyncio
    async def test_create_league(self, db_session: AsyncSession, sample_league_data):
        """Test creating a league."""
        league = League(**sample_league_data)
        db_session.add(league)
        await db_session.commit()
        await db_session.refresh(league)
        
        assert league.league_key == sample_league_data["league_key"]
        assert league.name == sample_league_data["name"]
        assert league.season == sample_league_data["season"]
        assert league.scoring_json == sample_league_data["scoring_json"]
        assert league.roster_slots_json == sample_league_data["roster_slots_json"]
        assert league.league_type == sample_league_data["league_type"]
        assert league.num_teams == sample_league_data["num_teams"]
        assert league.is_finished is False
    
    @pytest.mark.asyncio
    async def test_league_scoring_rules_property(self, db_session: AsyncSession, sample_league_data):
        """Test league scoring rules property."""
        league = League(**sample_league_data)
        db_session.add(league)
        await db_session.commit()
        await db_session.refresh(league)
        
        scoring_rules = league.scoring_rules
        assert isinstance(scoring_rules, dict)
        assert scoring_rules["passing_yards"] == 0.04
        assert scoring_rules["passing_tds"] == 4
    
    @pytest.mark.asyncio
    async def test_league_roster_slots_property(self, db_session: AsyncSession, sample_league_data):
        """Test league roster slots property."""
        league = League(**sample_league_data)
        db_session.add(league)
        await db_session.commit()
        await db_session.refresh(league)
        
        roster_slots = league.roster_slots
        assert isinstance(roster_slots, dict)
        assert roster_slots["QB"] == 1
        assert roster_slots["RB"] == 2
        assert roster_slots["WR"] == 2
        assert roster_slots["TE"] == 1
    
    @pytest.mark.asyncio
    async def test_create_team(self, db_session: AsyncSession, sample_league_data, sample_team_data):
        """Test creating a team."""
        # Create league first
        league = League(**sample_league_data)
        db_session.add(league)
        await db_session.commit()
        
        # Create team
        team = Team(**sample_team_data)
        db_session.add(team)
        await db_session.commit()
        await db_session.refresh(team)
        
        assert team.team_key == sample_team_data["team_key"]
        assert team.league_key == sample_team_data["league_key"]
        assert team.name == sample_team_data["name"]
        assert team.manager == sample_team_data["manager"]
        assert team.division_id == sample_team_data["division_id"]
        assert team.rank == sample_team_data["rank"]
        assert team.wins == sample_team_data["wins"]
        assert team.losses == sample_team_data["losses"]
        assert team.ties == sample_team_data["ties"]
    
    @pytest.mark.asyncio
    async def test_create_player(self, db_session: AsyncSession, sample_player_data):
        """Test creating a player."""
        player = Player(**sample_player_data)
        db_session.add(player)
        await db_session.commit()
        await db_session.refresh(player)
        
        assert player.player_id_yahoo == sample_player_data["player_id_yahoo"]
        assert player.gsis_id == sample_player_data["gsis_id"]
        assert player.pfr_id == sample_player_data["pfr_id"]
        assert player.full_name == sample_player_data["full_name"]
        assert player.first_name == sample_player_data["first_name"]
        assert player.last_name == sample_player_data["last_name"]
        assert player.position == sample_player_data["position"]
        assert player.team == sample_player_data["team"]
        assert player.bye_week == sample_player_data["bye_week"]
        assert player.is_active is True
    
    @pytest.mark.asyncio
    async def test_create_league_player(self, db_session: AsyncSession, sample_league_data, sample_player_data, sample_team_data):
        """Test creating a league player."""
        # Create league, team, and player
        league = League(**sample_league_data)
        db_session.add(league)
        
        team = Team(**sample_team_data)
        db_session.add(team)
        
        player = Player(**sample_player_data)
        db_session.add(player)
        
        await db_session.commit()
        
        # Create league player
        league_player = LeaguePlayer(
            league_key=sample_league_data["league_key"],
            player_id_yahoo=sample_player_data["player_id_yahoo"],
            status="FA",
            percent_rostered=45,
            faab_cost_est=5,
            owner_team_key=None
        )
        db_session.add(league_player)
        await db_session.commit()
        await db_session.refresh(league_player)
        
        assert league_player.league_key == sample_league_data["league_key"]
        assert league_player.player_id_yahoo == sample_player_data["player_id_yahoo"]
        assert league_player.status == "FA"
        assert league_player.percent_rostered == 45
        assert league_player.faab_cost_est == 5
        assert league_player.owner_team_key is None
    
    @pytest.mark.asyncio
    async def test_create_roster(self, db_session: AsyncSession, sample_team_data, sample_player_data):
        """Test creating a roster."""
        # Create team and player
        team = Team(**sample_team_data)
        db_session.add(team)
        
        player = Player(**sample_player_data)
        db_session.add(player)
        
        await db_session.commit()
        
        # Create roster
        roster = Roster(
            team_key=sample_team_data["team_key"],
            week=1,
            slot="QB",
            player_id_yahoo=sample_player_data["player_id_yahoo"],
            is_starting=True
        )
        db_session.add(roster)
        await db_session.commit()
        await db_session.refresh(roster)
        
        assert roster.team_key == sample_team_data["team_key"]
        assert roster.week == 1
        assert roster.slot == "QB"
        assert roster.player_id_yahoo == sample_player_data["player_id_yahoo"]
        assert roster.is_starting is True
    
    @pytest.mark.asyncio
    async def test_create_draft_pick(self, db_session: AsyncSession, sample_league_data, sample_team_data, sample_player_data):
        """Test creating a draft pick."""
        # Create league, team, and player
        league = League(**sample_league_data)
        db_session.add(league)
        
        team = Team(**sample_team_data)
        db_session.add(team)
        
        player = Player(**sample_player_data)
        db_session.add(player)
        
        await db_session.commit()
        
        # Create draft pick
        draft_pick = DraftPick(
            league_key=sample_league_data["league_key"],
            round=1,
            pick=1,
            team_key=sample_team_data["team_key"],
            player_id_yahoo=sample_player_data["player_id_yahoo"],
            cost=50
        )
        db_session.add(draft_pick)
        await db_session.commit()
        await db_session.refresh(draft_pick)
        
        assert draft_pick.league_key == sample_league_data["league_key"]
        assert draft_pick.round == 1
        assert draft_pick.pick == 1
        assert draft_pick.team_key == sample_team_data["team_key"]
        assert draft_pick.player_id_yahoo == sample_player_data["player_id_yahoo"]
        assert draft_pick.cost == 50


class TestNFLDataModels:
    """Test NFL data models."""
    
    @pytest.mark.asyncio
    async def test_create_weekly_stats(self, db_session: AsyncSession, sample_weekly_stats_data):
        """Test creating weekly stats."""
        stats = WeeklyStats(**sample_weekly_stats_data)
        db_session.add(stats)
        await db_session.commit()
        await db_session.refresh(stats)
        
        assert stats.gsis_id == sample_weekly_stats_data["gsis_id"]
        assert stats.season == sample_weekly_stats_data["season"]
        assert stats.week == sample_weekly_stats_data["week"]
        assert stats.stat_json == sample_weekly_stats_data["stat_json"]
        assert stats.team == sample_weekly_stats_data["team"]
        assert stats.opponent == sample_weekly_stats_data["opponent"]
        assert stats.game_date is not None
    
    @pytest.mark.asyncio
    async def test_weekly_stats_stats_property(self, db_session: AsyncSession, sample_weekly_stats_data):
        """Test weekly stats stats property."""
        stats = WeeklyStats(**sample_weekly_stats_data)
        db_session.add(stats)
        await db_session.commit()
        await db_session.refresh(stats)
        
        stats_dict = stats.stats
        assert isinstance(stats_dict, dict)
        assert stats_dict["passing_yards"] == 250
        assert stats_dict["passing_tds"] == 2
        assert stats_dict["interceptions"] == 1
    
    @pytest.mark.asyncio
    async def test_create_weekly_projections(self, db_session: AsyncSession):
        """Test creating weekly projections."""
        projection = WeeklyProjections(
            gsis_id="00-0012345",
            season=2024,
            week=1,
            source="test",
            proj_json='{"passing_yards": 275, "passing_tds": 2.5}',
            created_at=datetime.now(timezone.utc),
            confidence=0.85
        )
        db_session.add(projection)
        await db_session.commit()
        await db_session.refresh(projection)
        
        assert projection.gsis_id == "00-0012345"
        assert projection.season == 2024
        assert projection.week == 1
        assert projection.source == "test"
        assert projection.proj_json == '{"passing_yards": 275, "passing_tds": 2.5}'
        assert projection.confidence == 0.85
    
    @pytest.mark.asyncio
    async def test_weekly_projections_projection_property(self, db_session: AsyncSession):
        """Test weekly projections projection property."""
        projection = WeeklyProjections(
            gsis_id="00-0012345",
            season=2024,
            week=1,
            source="test",
            proj_json='{"passing_yards": 275, "passing_tds": 2.5}',
            created_at=datetime.now(timezone.utc),
            confidence=0.85
        )
        db_session.add(projection)
        await db_session.commit()
        await db_session.refresh(projection)
        
        proj_dict = projection.projections
        assert isinstance(proj_dict, dict)
        assert proj_dict["passing_yards"] == 275
        assert proj_dict["passing_tds"] == 2.5
    
    @pytest.mark.asyncio
    async def test_create_injuries(self, db_session: AsyncSession):
        """Test creating injuries."""
        injury = Injuries(
            gsis_id="00-0012345",
            week=1,
            season=2024,
            status="Questionable",
            report="Knee injury",
            practice_status="Limited",
            team="TEST",
            position="QB"
        )
        db_session.add(injury)
        await db_session.commit()
        await db_session.refresh(injury)
        
        assert injury.gsis_id == "00-0012345"
        assert injury.week == 1
        assert injury.season == 2024
        assert injury.status == "Questionable"
        assert injury.report == "Knee injury"
        assert injury.practice_status == "Limited"
        assert injury.team == "TEST"
        assert injury.position == "QB"
    
    @pytest.mark.asyncio
    async def test_create_depth_charts(self, db_session: AsyncSession):
        """Test creating depth charts."""
        depth_chart = DepthCharts(
            team="TEST",
            week=1,
            season=2024,
            position="QB",
            gsis_id="00-0012345",
            depth_order=1,
            role="Starter"
        )
        db_session.add(depth_chart)
        await db_session.commit()
        await db_session.refresh(depth_chart)
        
        assert depth_chart.team == "TEST"
        assert depth_chart.week == 1
        assert depth_chart.season == 2024
        assert depth_chart.position == "QB"
        assert depth_chart.gsis_id == "00-0012345"
        assert depth_chart.depth_order == 1
        assert depth_chart.role == "Starter"
    
    @pytest.mark.asyncio
    async def test_create_player_id_mapping(self, db_session: AsyncSession):
        """Test creating player ID mapping."""
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
        await db_session.refresh(mapping)
        
        assert mapping.gsis_id == "00-0012345"
        assert mapping.pfr_id == "P123456"
        assert mapping.espn_id == "12345"
        assert mapping.full_name == "Test Player"
        assert mapping.first_name == "Test"
        assert mapping.last_name == "Player"
        assert mapping.position == "QB"
        assert mapping.team == "TEST"
        assert mapping.is_active is True
        assert mapping.confidence == 0.95
    
    @pytest.mark.asyncio
    async def test_create_recommendations(self, db_session: AsyncSession):
        """Test creating recommendations."""
        recommendation = Recommendations(
            team_key="414.l.123456.t.1",
            week=1,
            season=2024,
            lineup_json='{"QB": "414.p.12345", "RB1": "414.p.12346"}',
            delta_points=2.5,
            algorithm_version="v1.0",
            confidence=0.85,
            reasoning="Better matchup for QB"
        )
        db_session.add(recommendation)
        await db_session.commit()
        await db_session.refresh(recommendation)
        
        assert recommendation.team_key == "414.l.123456.t.1"
        assert recommendation.week == 1
        assert recommendation.season == 2024
        assert recommendation.lineup_json == '{"QB": "414.p.12345", "RB1": "414.p.12346"}'
        assert recommendation.delta_points == 2.5
        assert recommendation.algorithm_version == "v1.0"
        assert recommendation.confidence == 0.85
        assert recommendation.reasoning == "Better matchup for QB"
    
    @pytest.mark.asyncio
    async def test_recommendations_lineup_property(self, db_session: AsyncSession):
        """Test recommendations lineup property."""
        recommendation = Recommendations(
            team_key="414.l.123456.t.1",
            week=1,
            season=2024,
            lineup_json='{"QB": "414.p.12345", "RB1": "414.p.12346"}',
            delta_points=2.5,
            algorithm_version="v1.0",
            confidence=0.85,
            reasoning="Better matchup for QB"
        )
        db_session.add(recommendation)
        await db_session.commit()
        await db_session.refresh(recommendation)
        
        lineup_dict = recommendation.lineup
        assert isinstance(lineup_dict, dict)
        assert lineup_dict["QB"] == "414.p.12345"
        assert lineup_dict["RB1"] == "414.p.12346"

