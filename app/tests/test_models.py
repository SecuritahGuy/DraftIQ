import json
from datetime import datetime, timedelta

from app.models.fantasy import League
from app.models.user import YahooToken


def test_league_scoring_and_roster_properties():
    league = League(
        league_key="414.l.123456",
        name="Test League",
        season=2024,
        scoring_json=json.dumps({"pass_td": 6}),
        roster_slots_json=json.dumps({"QB": 1, "RB": 2}),
    )

    assert league.scoring_rules == {"pass_td": 6}
    assert league.roster_slots == {"QB": 1, "RB": 2}


def test_yahoo_token_expiration_properties():
    token = YahooToken(
        id="token1",
        user_id="user1",
        access_token="access",
        refresh_token="refresh",
        expires_at=datetime.utcnow() + timedelta(minutes=10),
    )
    assert token.is_expired is False
    assert token.needs_refresh is False

    expiring_token = YahooToken(
        id="token2",
        user_id="user1",
        access_token="access",
        refresh_token="refresh",
        expires_at=datetime.utcnow() + timedelta(minutes=4),
    )
    assert expiring_token.needs_refresh is True

    expired_token = YahooToken(
        id="token3",
        user_id="user1",
        access_token="access",
        refresh_token="refresh",
        expires_at=datetime.utcnow() - timedelta(minutes=1),
    )
    assert expired_token.is_expired is True
