"""Tests for the PDF drop-folder watcher (ingestion/watch_pdfs.py)."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Helpers used in tests
# ---------------------------------------------------------------------------

def _write_processed_log(watch_dir: Path, paths: list[Path]) -> None:
    log = watch_dir / ".processed_pdfs"
    log.write_text("\n".join(str(p.resolve()) for p in paths) + "\n")


# ---------------------------------------------------------------------------
# Unit tests
# ---------------------------------------------------------------------------

def test_find_pdfs_empty_dir():
    from ingestion.watch_pdfs import _find_pdfs
    with tempfile.TemporaryDirectory() as tmp:
        result = _find_pdfs(Path(tmp))
    assert result == []


def test_find_pdfs_returns_pdfs():
    from ingestion.watch_pdfs import _find_pdfs
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp)
        (p / "match_01.pdf").touch()
        (p / "match_02.pdf").touch()
        (p / "readme.txt").touch()
        found = _find_pdfs(p)
    assert len(found) == 2
    assert all(f.suffix == ".pdf" for f in found)


def test_find_pdfs_nonexistent_dir():
    from ingestion.watch_pdfs import _find_pdfs
    result = _find_pdfs(Path("/nonexistent/path/that/does/not/exist"))
    assert result == []


def test_load_processed_empty():
    from ingestion.watch_pdfs import _load_processed
    with tempfile.TemporaryDirectory() as tmp:
        result = _load_processed(Path(tmp))
    assert result == set()


def test_load_processed_reads_log():
    from ingestion.watch_pdfs import _load_processed, _mark_processed
    with tempfile.TemporaryDirectory() as tmp:
        watch_dir = Path(tmp)
        dummy = watch_dir / "match_01.pdf"
        dummy.touch()
        _mark_processed(watch_dir, dummy)
        loaded = _load_processed(watch_dir)
    assert str(dummy.resolve()) in loaded


def test_mark_processed_appends():
    from ingestion.watch_pdfs import _mark_processed, _load_processed
    with tempfile.TemporaryDirectory() as tmp:
        watch_dir = Path(tmp)
        p1 = watch_dir / "a.pdf"
        p2 = watch_dir / "b.pdf"
        p1.touch()
        p2.touch()
        _mark_processed(watch_dir, p1)
        _mark_processed(watch_dir, p2)
        loaded = _load_processed(watch_dir)
    assert str(p1.resolve()) in loaded
    assert str(p2.resolve()) in loaded


def test_db_dsn_defaults():
    from ingestion.watch_pdfs import _db_dsn
    env = {
        "MYSQL_USER": "testuser",
        "MYSQL_PASSWORD": "testpass",
        "MYSQL_HOST": "localhost",
        "MYSQL_PORT": "3306",
        "MYSQL_DATABASE": "testdb",
    }
    with patch.dict(os.environ, env, clear=False):
        dsn = _db_dsn()
    assert "testuser" in dsn
    assert "testpass" in dsn
    assert "localhost" in dsn
    assert "testdb" in dsn


def test_watch_dir_from_env():
    from ingestion.watch_pdfs import _watch_dir
    with tempfile.TemporaryDirectory() as tmp:
        with patch.dict(os.environ, {"PDF_WATCH_DIR": tmp}, clear=False):
            result = _watch_dir()
    assert result == Path(tmp).resolve()


def test_main_no_pdfs_returns_zero():
    """main() returns 0 when the watch dir is empty."""
    from ingestion.watch_pdfs import main
    with tempfile.TemporaryDirectory() as tmp:
        ret = main(["--dir", tmp])
    assert ret == 0


def test_main_dry_run_marks_nothing():
    """In dry-run mode, no PDFs are marked as processed."""
    from ingestion.watch_pdfs import main, _load_processed

    with tempfile.TemporaryDirectory() as tmp:
        watch_dir = Path(tmp)
        pdf = watch_dir / "match_01.pdf"
        pdf.touch()

        mock_data = MagicMock()
        mock_data.match_no = 1
        mock_data.team_a_slug = "ger"
        mock_data.team_b_slug = "cur"
        mock_data.score_a = 7
        mock_data.score_b = 1
        mock_data.phases_a = []
        mock_data.phases_b = []

        with patch("ingestion.watch_pdfs._ingest_pdf", return_value=True) as mock_ingest:
            ret = main(["--dir", tmp, "--dry-run"])

        # dry-run still calls _ingest_pdf (which internally skips DB write)
        assert mock_ingest.called
        # nothing written to processed log
        processed = _load_processed(watch_dir)
    assert processed == set()


def test_main_processes_new_pdfs():
    """main() marks PDFs as processed after successful ingestion."""
    from ingestion.watch_pdfs import main, _load_processed

    with tempfile.TemporaryDirectory() as tmp:
        watch_dir = Path(tmp)
        pdf = watch_dir / "match_01.pdf"
        pdf.touch()

        with patch("ingestion.watch_pdfs._ingest_pdf", return_value=True):
            ret = main(["--dir", tmp])

        processed = _load_processed(watch_dir)

    assert str(pdf.resolve()) in processed
    assert ret == 0


def test_main_skips_already_processed():
    """PDFs already in the log are not re-ingested."""
    from ingestion.watch_pdfs import main, _mark_processed

    with tempfile.TemporaryDirectory() as tmp:
        watch_dir = Path(tmp)
        pdf = watch_dir / "match_01.pdf"
        pdf.touch()
        _mark_processed(watch_dir, pdf)

        with patch("ingestion.watch_pdfs._ingest_pdf", return_value=True) as mock_ingest:
            ret = main(["--dir", tmp])

        assert not mock_ingest.called
    assert ret == 0


def test_main_force_reprocesses():
    """--force causes already-processed PDFs to be re-ingested."""
    from ingestion.watch_pdfs import main, _mark_processed

    with tempfile.TemporaryDirectory() as tmp:
        watch_dir = Path(tmp)
        pdf = watch_dir / "match_01.pdf"
        pdf.touch()
        _mark_processed(watch_dir, pdf)

        with patch("ingestion.watch_pdfs._ingest_pdf", return_value=True) as mock_ingest:
            main(["--dir", tmp, "--force"])

        assert mock_ingest.called


def test_main_returns_one_on_failure():
    """main() returns 1 when at least one PDF fails ingestion."""
    from ingestion.watch_pdfs import main

    with tempfile.TemporaryDirectory() as tmp:
        watch_dir = Path(tmp)
        pdf = watch_dir / "broken.pdf"
        pdf.touch()

        with patch("ingestion.watch_pdfs._ingest_pdf", return_value=False):
            ret = main(["--dir", tmp])

    assert ret == 1
