import pandas as pd
import pytest
from unittest.mock import AsyncMock, MagicMock, call


@pytest.fixture
def mock_session():
    session = AsyncMock()
    result = MagicMock()
    result.rowcount = 1
    session.execute.return_value = result
    return session


@pytest.mark.asyncio
async def test_upsert_team_stats_empty_df(mock_session):
    from ingestion.load import upsert_team_stats

    affected = await upsert_team_stats(mock_session, pd.DataFrame(), 1, 10, "match")
    assert affected == 0
    mock_session.execute.assert_not_called()


@pytest.mark.asyncio
async def test_upsert_team_stats_calls_execute(mock_session):
    from ingestion.load import upsert_team_stats

    df = pd.DataFrame({
        "team_name": ["Germany"],
        "possession_pct": [57.8],
        "in_contest_pct": [6.9],
    })
    affected = await upsert_team_stats(mock_session, df, 1, 10, "match")
    assert affected == 1
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_upsert_phases_empty(mock_session):
    from ingestion.load import upsert_phases

    affected = await upsert_phases(mock_session, None, 1, 10)
    assert affected == 0


@pytest.mark.asyncio
async def test_upsert_line_breaks(mock_session):
    from ingestion.load import upsert_line_breaks

    df = pd.DataFrame({
        "team_name": ["Germany"],
        "line_type": ["Defensive"],
        "breaks_for": [12],
        "breaks_against": [5],
    })
    affected = await upsert_line_breaks(mock_session, df, 1, 10)
    assert affected == 1
