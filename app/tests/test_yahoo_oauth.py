import urllib.parse
from datetime import datetime

from app.services.yahoo_oauth import YahooOAuthService


def test_get_authorization_url_includes_query_params():
    """Authorization URL should contain required query parameters."""
    service = YahooOAuthService()
    state = "teststate"

    url = service.get_authorization_url(state)
    parsed = urllib.parse.urlparse(url)
    query = urllib.parse.parse_qs(parsed.query)

    assert query["client_id"][0] == service.client_id
    assert query["redirect_uri"][0] == service.redirect_uri
    assert query["response_type"][0] == "code"
    assert query["state"][0] == state
    assert query["scope"][0] == "fspt-r"


def test_parse_token_response_calculates_expiration():
    """Token parsing should calculate expiration datetime in the future."""
    service = YahooOAuthService()
    token_data = {
        "access_token": "access",
        "refresh_token": "refresh",
        "expires_in": 3600,
        "token_type": "Bearer",
        "scope": "fspt-r",
    }

    parsed = service.parse_token_response(token_data)

    assert parsed["access_token"] == token_data["access_token"]
    assert parsed["refresh_token"] == token_data["refresh_token"]
    assert parsed["token_type"] == token_data["token_type"]
    assert parsed["scope"] == token_data["scope"]
    assert parsed["expires_in"] == token_data["expires_in"]
    assert isinstance(parsed["expires_at"], datetime)
    assert parsed["expires_at"] > datetime.utcnow()
