import httpx
import pytest

from app.services.yahoo_api import YahooAPIClient


@pytest.mark.asyncio
async def test_make_request_returns_json(monkeypatch):
    """_make_request should return parsed JSON from the API."""
    expected_url = "https://fantasysports.yahooapis.com/fantasy/v2/test"
    response_data = {"ok": True}

    class MockAsyncClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

        async def get(self, url, headers=None, params=None):
            assert url == expected_url
            request = httpx.Request("GET", url)
            return httpx.Response(200, json=response_data, request=request)

    monkeypatch.setattr(httpx, "AsyncClient", lambda: MockAsyncClient())

    client = YahooAPIClient("token")
    data = await client._make_request("test")
    assert data == response_data


@pytest.mark.asyncio
async def test_get_user_leagues_parses_response(monkeypatch):
    """get_user_leagues should extract leagues from API response."""
    api_response = {
        "fantasy_content": {
            "users": {
                "0": {
                    "user": {
                        "games": {
                            "0": {
                                "leagues": {
                                    "0": {
                                        "league": {
                                            "id": "1",
                                            "name": "League1",
                                        }
                                    },
                                    "1": {
                                        "league": {
                                            "id": "2",
                                            "name": "League2",
                                        }
                                    },
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    async def mock_make_request(self, endpoint: str, params=None):
        assert endpoint == "users;use_login=1/games;game_keys=nfl/leagues"
        return api_response

    monkeypatch.setattr(YahooAPIClient, "_make_request", mock_make_request)

    client = YahooAPIClient("token")
    leagues = await client.get_user_leagues()
    assert leagues == [
        {"id": "1", "name": "League1"},
        {"id": "2", "name": "League2"},
    ]
