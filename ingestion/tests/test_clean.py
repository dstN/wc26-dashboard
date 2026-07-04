import pandas as pd
import pytest

from ingestion.clean import clean


def test_pct_columns_converted():
    df = pd.DataFrame({
        "team_name": ["Germany"],
        "possession_pct": ["57.8%"],
        "in_contest_pct": ["6.9%"],
        "out_of_possession_pct": ["35.3%"],
    })
    result = clean(df)
    assert result["possession_pct"].iloc[0] == pytest.approx(57.8)
    assert result["in_contest_pct"].iloc[0] == pytest.approx(6.9)
    assert result["out_of_possession_pct"].iloc[0] == pytest.approx(35.3)


def test_int_columns_converted():
    df = pd.DataFrame({
        "team_name": ["Germany"],
        "goals": [7.0],
        "shots": [14.0],
    })
    result = clean(df)
    assert result["goals"].iloc[0] == 7
    assert result["goals"].iloc[0] == 7  # np.int64 is int-like


def test_float_columns_converted():
    df = pd.DataFrame({
        "team_name": ["Germany"],
        "xg": ["3.1"],
        "recovery_speed": ["4.2"],
    })
    result = clean(df)
    assert result["xg"].iloc[0] == pytest.approx(3.1)
    assert result["recovery_speed"].iloc[0] == pytest.approx(4.2)


def test_null_rows_dropped():
    df = pd.DataFrame({
        "team_name": [None, None],
        "goals": [None, None],
    })
    result = clean(df)
    assert len(result) == 0


def test_team_name_whitespace_normalised():
    df = pd.DataFrame({"team_name": ["  Germany  "]})
    result = clean(df)
    assert result["team_name"].iloc[0] == "Germany"


def test_pct_without_sign():
    df = pd.DataFrame({"team_name": ["X"], "possession_pct": ["57.8"]})
    result = clean(df)
    assert result["possession_pct"].iloc[0] == pytest.approx(57.8)
