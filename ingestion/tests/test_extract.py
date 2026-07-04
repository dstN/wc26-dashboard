from pathlib import Path

import pandas as pd
import pytest
from unittest.mock import AsyncMock, patch

from ingestion.extract import extract, _first_matching, _GENERAL_COLS, _LINE_BREAKS_COLS

FIXTURES = Path(__file__).parent / "fixtures" / "html"


def _read_html(filename: str) -> list[pd.DataFrame]:
    path = FIXTURES / filename
    return pd.read_html(str(path), flavor="lxml")


class TestFirstMatching:
    def test_finds_exact_match(self):
        tables = _read_html("germany_general.html")
        df = _first_matching(tables, _GENERAL_COLS)
        assert df is not None
        assert "possession_pct" in df.columns
        assert "team_name" in df.columns

    def test_finds_line_breaks(self):
        tables = _read_html("germany_line_breaks.html")
        df = _first_matching(tables, _LINE_BREAKS_COLS)
        assert df is not None
        assert set(df.columns) == {"team_name", "line_type", "breaks_for", "breaks_against"}

    def test_returns_none_for_no_match(self):
        empty = [pd.DataFrame({"foo": [1], "bar": [2]})]
        result = _first_matching(empty, _GENERAL_COLS)
        assert result is None


@pytest.mark.asyncio
async def test_extract_general_uses_fast_path():
    tables = _read_html("germany_general.html")
    with patch("ingestion.extract.fetch_tables", new=AsyncMock(return_value=tables)):
        df = await extract("http://fake/germany", "general")
    assert df is not None
    assert len(df) == 2
    assert df.iloc[0]["team_name"] == "Germany"


@pytest.mark.asyncio
async def test_extract_falls_back_to_playwright():
    tables = _read_html("germany_general.html")
    with (
        patch("ingestion.extract.fetch_tables", new=AsyncMock(return_value=None)),
        patch("ingestion.extract.render_tables", new=AsyncMock(return_value=tables)),
    ):
        df = await extract("http://fake/germany", "general")
    assert df is not None
    assert len(df) == 2


@pytest.mark.asyncio
async def test_extract_returns_none_when_both_fail():
    with (
        patch("ingestion.extract.fetch_tables", new=AsyncMock(return_value=None)),
        patch("ingestion.extract.render_tables", new=AsyncMock(return_value=None)),
    ):
        df = await extract("http://fake/germany", "general")
    assert df is None
