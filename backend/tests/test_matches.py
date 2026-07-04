import pytest
import pytest_asyncio
from sqlalchemy import text


@pytest_asyncio.fixture
async def seeded_match_10(db_session):
    """Insert minimal Germany vs Curaçao match 10 data for tests."""
    await db_session.execute(text(
        "INSERT IGNORE INTO teams (team_id, team_name, team_slug, group_name, color_primary) "
        "VALUES (1, 'Germany', 'germany', 'E', '#000000'), "
        "       (2, 'Curaçao', 'curacao', 'E', '#0072CE')"
    ))
    await db_session.execute(text(
        "INSERT IGNORE INTO matches (match_id, match_number, group_name, stage, "
        "home_team_id, away_team_id, home_score, away_score, match_date, venue, city) "
        "VALUES (10, 10, 'E', 'Group', 1, 2, 7, 1, '2026-06-14', 'NRG Stadium', 'Houston')"
    ))
    await db_session.execute(text(
        "INSERT IGNORE INTO match_stats "
        "(team_id, match_id, scope, possession_pct, in_contest_pct, out_of_possession_pct, xg, goals) "
        "VALUES (1, 10, 'match', 57.8, 6.9, 35.3, 3.1, 7), "
        "       (2, 10, 'match', 35.3, 6.9, 57.8, 0.4, 1)"
    ))
    await db_session.flush()
    yield


@pytest.mark.asyncio
async def test_dashboard_returns_200(client, seeded_match_10):
    resp = await client.get("/api/v1/dashboard?match_id=10")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_dashboard_possession_values(client, seeded_match_10):
    resp = await client.get("/api/v1/dashboard?match_id=10")
    assert resp.status_code == 200
    data = resp.json()
    poss = data["possession"]
    team_a = poss["team_a"]
    assert team_a["possession_pct"] == pytest.approx(57.8)
    assert team_a["in_contest_pct"] == pytest.approx(6.9)
    assert team_a["out_of_possession_pct"] == pytest.approx(35.3)


@pytest.mark.asyncio
async def test_dashboard_has_required_keys(client, seeded_match_10):
    resp = await client.get("/api/v1/dashboard?match_id=10")
    data = resp.json()
    required = {"overview", "featured", "possession", "head_to_head", "phases", "kpi_cards"}
    assert required.issubset(set(data.keys()))


@pytest.mark.asyncio
async def test_dashboard_404_for_unknown_match(client, create_tables):
    resp = await client.get("/api/v1/dashboard?match_id=9999")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_health_endpoint(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_possession_endpoint(client, seeded_match_10):
    resp = await client.get("/api/v1/matches/10/possession")
    assert resp.status_code == 200
    data = resp.json()
    assert "team_a" in data
    assert "team_b" in data
    assert data["team_a"]["possession_pct"] == pytest.approx(57.8)
