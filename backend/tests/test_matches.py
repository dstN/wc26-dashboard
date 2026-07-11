import pytest
import pytest_asyncio
from sqlalchemy import text


@pytest_asyncio.fixture
async def seeded_match_10(db_session):
    """Insert minimal Germany vs Curaçao match 10 data for tests."""
    await db_session.execute(text(
        "INSERT INTO teams (id, name, short_code, slug, color, group_letter) "
        "VALUES (1, 'Germany', 'GER', 'germany', '--c-yellow', 'E'), "
        "       (2, 'Curaçao', 'CUW', 'curacao', '--c-blue', 'E')"
    ))
    await db_session.execute(text(
        "INSERT INTO matches (id, match_no, team_a_id, team_b_id, score_a, score_b, "
        "venue, match_date, group_letter) "
        "VALUES (10, 10, 1, 2, 7, 1, 'NRG Stadium', '2026-06-14', 'E')"
    ))
    await db_session.execute(text(
        "INSERT INTO match_stats (team_id, match_id, scope, possession_team_a, "
        "possession_team_b, possession_in_contest, xg_a, xg_b, goals_a, goals_b) "
        "VALUES (1, 10, 'match', 57.8, 35.3, 6.9, 4.17, 0.40, 7, 1)"
    ))
    # get_match_dashboard resolves defensive stats with scalar_one() — one row
    # per team is required, or the dashboard 404s.
    await db_session.execute(text(
        "INSERT INTO defensive_actions (team_id, match_id, scope, forced_turnovers, "
        "pressure_on_ball) "
        "VALUES (1, 10, 'match', 12, 'heavy'), (2, 10, 'match', 5, 'moderate')"
    ))
    await db_session.flush()
    yield


@pytest.mark.asyncio
async def test_dashboard_returns_200(client, seeded_match_10):
    resp = await client.get("/api/v1/dashboard")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_dashboard_possession_values(client, seeded_match_10):
    resp = await client.get("/api/v1/dashboard")
    assert resp.status_code == 200
    poss = resp.json()["possession"]
    assert poss["possession_team_a"] == pytest.approx(57.8)
    assert poss["possession_team_b"] == pytest.approx(35.3)
    assert poss["possession_in_contest"] == pytest.approx(6.9)


@pytest.mark.asyncio
async def test_dashboard_has_required_keys(client, seeded_match_10):
    resp = await client.get("/api/v1/dashboard")
    data = resp.json()
    required = {
        "overview", "featured", "possession", "head_to_head", "phases",
        "spatial", "line_breaks", "final_third", "defensive", "kpi_cards",
    }
    assert required.issubset(set(data.keys()))


@pytest.mark.asyncio
async def test_dashboard_featured_is_latest_match(client, seeded_match_10):
    resp = await client.get("/api/v1/dashboard")
    featured = resp.json()["featured"]
    assert featured["id"] == 10
    assert featured["score_a"] == 7
    assert featured["score_b"] == 1
    assert featured["went_to_extra_time"] is False
    assert featured["penalty_score_a"] is None


@pytest.mark.asyncio
async def test_dashboard_404_on_empty_db(client, create_tables):
    resp = await client.get("/api/v1/dashboard")
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
    assert data["possession_team_a"] == pytest.approx(57.8)
    assert data["possession_team_b"] == pytest.approx(35.3)


@pytest.mark.asyncio
async def test_match_404_for_unknown_id(client, seeded_match_10):
    resp = await client.get("/api/v1/matches/9999")
    assert resp.status_code == 404
