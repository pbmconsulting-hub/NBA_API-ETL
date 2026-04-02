"""tests/test_api/test_integration.py – Integration tests for the FastAPI API."""
import pytest


def _skip_if_no_fastapi():
    try:
        import fastapi  # noqa: F401
        import httpx  # noqa: F401
    except ImportError:
        pytest.skip("fastapi or httpx not installed")


def _make_client():
    """Create an httpx.AsyncClient using ASGITransport for the FastAPI app."""
    import httpx
    from api.main import app
    transport = httpx.ASGITransport(app=app)
    return httpx.AsyncClient(transport=transport, base_url="http://test")


class TestHealthEndpoint:
    @pytest.mark.asyncio
    async def test_health_schema(self):
        _skip_if_no_fastapi()
        async with _make_client() as client:
            resp = await client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert "status" in data
        assert data["status"] in ("healthy", "degraded")
        assert "timestamp" in data

    @pytest.mark.asyncio
    async def test_health_has_version_when_healthy(self):
        _skip_if_no_fastapi()
        async with _make_client() as client:
            resp = await client.get("/health")
        data = resp.json()
        if data["status"] == "healthy":
            assert "version" in data


class TestPredictionsEndpoint:
    @pytest.mark.asyncio
    async def test_today_predictions_returns_list(self):
        _skip_if_no_fastapi()
        async with _make_client() as client:
            resp = await client.get("/predictions/today")
        assert resp.status_code == 200
        data = resp.json()
        assert "date" in data
        assert "predictions" in data
        assert isinstance(data["predictions"], list)

    @pytest.mark.asyncio
    async def test_predictions_by_date_valid(self):
        _skip_if_no_fastapi()
        async with _make_client() as client:
            resp = await client.get("/predictions/2025-01-15")
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_predictions_by_date_invalid(self):
        _skip_if_no_fastapi()
        async with _make_client() as client:
            resp = await client.get("/predictions/not-a-date")
        assert resp.status_code == 400


class TestPlayersEndpoint:
    @pytest.mark.asyncio
    async def test_player_stats_not_found(self):
        _skip_if_no_fastapi()
        async with _make_client() as client:
            resp = await client.get("/players/Nonexistent%20Player%20XYZ/stats")
        # Either 404 or 200 with empty data is acceptable
        assert resp.status_code in (200, 404)
