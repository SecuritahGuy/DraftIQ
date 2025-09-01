"""
Test configuration and fixtures.
"""

import pytest
import pytest_asyncio
import asyncio
from typing import AsyncGenerator, Generator
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from httpx import AsyncClient, ASGITransport

from app.core.database import get_db, Base
from app.core.config import settings
from app.main import app


# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=StaticPool,
    connect_args={"check_same_thread": False},
    echo=False,
)

# Create test session maker
TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    # Create all tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session
    async with TestSessionLocal() as session:
        yield session
    
    # Drop all tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client with database dependency override."""
    
    def override_get_db():
        return db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "id": "test-user-123",
        "email": "test@example.com",
        "username": "testuser",
        "is_active": True,
        "is_verified": True,
        "display_name": "Test User"
    }


@pytest.fixture
def sample_yahoo_token_data():
    """Sample Yahoo token data for testing."""
    return {
        "id": "test-token-123",
        "user_id": "test-user-123",
        "access_token": "test-access-token",
        "refresh_token": "test-refresh-token",
        "expires_at": datetime(2024, 12, 31, 23, 59, 59, tzinfo=timezone.utc),
        "token_type": "Bearer",
        "scope": "read",
        "yahoo_user_id": "yahoo-user-123",
        "yahoo_guid": "yahoo-guid-123"
    }


@pytest.fixture
def sample_league_data():
    """Sample league data for testing."""
    return {
        "league_key": "414.l.123456",
        "name": "Test League",
        "season": 2024,
        "scoring_json": '{"passing_yards": 0.04, "passing_tds": 4}',
        "roster_slots_json": '{"QB": 1, "RB": 2, "WR": 2, "TE": 1, "FLEX": 1, "K": 1, "DEF": 1}',
        "league_type": "standard",
        "num_teams": 12,
        "is_finished": False
    }


@pytest.fixture
def sample_team_data():
    """Sample team data for testing."""
    return {
        "team_key": "414.l.123456.t.1",
        "league_key": "414.l.123456",
        "name": "Test Team",
        "manager": "Test Manager",
        "division_id": 1,
        "rank": 1,
        "wins": 8,
        "losses": 4,
        "ties": 0
    }


@pytest.fixture
def sample_player_data():
    """Sample player data for testing."""
    return {
        "player_id_yahoo": "414.p.12345",
        "gsis_id": "00-0012345",
        "pfr_id": "P123456",
        "full_name": "Test Player",
        "first_name": "Test",
        "last_name": "Player",
        "position": "QB",
        "team": "TEST",
        "bye_week": 8,
        "is_active": True
    }


@pytest.fixture
def sample_weekly_stats_data():
    """Sample weekly stats data for testing."""
    return {
        "gsis_id": "00-0012345",
        "season": 2024,
        "week": 1,
        "stat_json": '{"passing_yards": 250, "passing_tds": 2, "interceptions": 1}',
        "team": "TEST",
        "opponent": "OPP",
        "game_date": datetime(2024, 9, 8, 13, 0, 0, tzinfo=timezone.utc)
    }
