#!/usr/bin/env python3
"""
PDF Drop Folder Watcher — EFI WC26 Dashboard
=============================================
Scans a configurable directory for new PMSR PDF files and ingests any that
have not yet been processed.

Designed for cron-based invocation on Apache / Phusion Passenger deployments.
No daemon process is required — run this script on a schedule:

    # Example crontab entry (every 5 minutes) — note: run from the ingestion/
    # directory (the package root), not the repo root:
    */5 * * * * cd /path/to/project/ingestion && python -m ingestion.watch_pdfs >> /var/log/efi_watch.log 2>&1

Environment variables (set in .env or shell):
    PDF_WATCH_DIR   Path to the folder where new PDFs are dropped.
                    Default: ./pdfs
    MYSQL_HOST      Database host (default: localhost)
    MYSQL_PORT      Database port (default: 3306)
    MYSQL_DATABASE  Database name (default: wc26)
    MYSQL_USER      Database user (default: wc26user)
    MYSQL_PASSWORD  Database password (default: wc26pass)

Processed-file tracking:
    A file named .processed_pdfs is written inside PDF_WATCH_DIR.
    Each line contains an absolute path of a successfully ingested PDF.
    Re-running the watcher on already-processed files is safe (idempotent
    SQL uses INSERT … ON DUPLICATE KEY UPDATE) but skipped for speed.

Usage:
    python -m ingestion.watch_pdfs               # process all new PDFs
    python -m ingestion.watch_pdfs --dry-run     # parse only, no DB writes
    python -m ingestion.watch_pdfs --force       # re-process all PDFs
    python -m ingestion.watch_pdfs --dir /path   # override PDF_WATCH_DIR
"""

from __future__ import annotations

import argparse
import logging
import os
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("efi.watch")


# ---------------------------------------------------------------------------
# Config helpers
# ---------------------------------------------------------------------------

def _watch_dir() -> Path:
    raw = os.environ.get("PDF_WATCH_DIR", "./pdfs")
    p = Path(raw).expanduser().resolve()
    return p


def _db_dsn() -> str:
    user = os.environ.get("MYSQL_USER", "wc26user")
    pw   = os.environ.get("MYSQL_PASSWORD", "wc26pass")
    host = os.environ.get("MYSQL_HOST", "localhost")
    port = os.environ.get("MYSQL_PORT", "3306")
    db   = os.environ.get("MYSQL_DATABASE", "wc26")
    return f"mysql+pymysql://{user}:{pw}@{host}:{port}/{db}"


# ---------------------------------------------------------------------------
# Processed-file log
# ---------------------------------------------------------------------------
PROCESSED_LOG_NAME = ".processed_pdfs"


def _load_processed(watch_dir: Path) -> set[str]:
    log_file = watch_dir / PROCESSED_LOG_NAME
    if not log_file.exists():
        return set()
    lines = log_file.read_text(encoding="utf-8").splitlines()
    return {l.strip() for l in lines if l.strip()}


def _mark_processed(watch_dir: Path, pdf_path: Path) -> None:
    log_file = watch_dir / PROCESSED_LOG_NAME
    with log_file.open("a", encoding="utf-8") as fh:
        fh.write(str(pdf_path.resolve()) + "\n")


# ---------------------------------------------------------------------------
# PDF discovery
# ---------------------------------------------------------------------------

def _find_pdfs(watch_dir: Path) -> list[Path]:
    if not watch_dir.exists():
        logger.warning("Watch directory does not exist: %s", watch_dir)
        return []
    return sorted(watch_dir.glob("*.pdf"))


# ---------------------------------------------------------------------------
# Ingestion
# ---------------------------------------------------------------------------

def _ingest_pdf(pdf_path: Path, dry_run: bool) -> bool:
    """
    Parse a single PDF via the sanctioned PMSR pipeline
    (parse_pmsr + pmsr_to_sql) and write the SQL to the database.
    Returns True on success, False on failure.
    """
    from ingestion.pmsr_to_sql import pdf_to_sql

    logger.info("Parsing  %s …", pdf_path.name)
    try:
        sql = pdf_to_sql(str(pdf_path))
    except Exception as exc:
        logger.error("Parse failed for %s: %s", pdf_path.name, exc)
        return False

    # First generated line is a "-- ── GER 7–1 CUR · Match 10 · …" header comment.
    header = sql.splitlines()[0].lstrip("- ").strip() if sql else ""
    logger.info("  → %s", header)

    if dry_run:
        logger.info("  [dry-run] skipping DB write")
        return True

    return _execute_sql(sql, pdf_path.name)


def _execute_sql(sql: str, label: str) -> bool:
    """Execute SQL statements against the configured database."""
    try:
        import sqlalchemy as sa  # type: ignore
    except ImportError:
        logger.error("sqlalchemy not installed — cannot write to database")
        return False

    dsn = _db_dsn()
    engine = sa.create_engine(dsn, echo=False)
    try:
        with engine.connect() as conn:
            # Generated SQL terminates every statement with ";" at end-of-line,
            # so split there instead of on every ";" (values may contain one).
            for fragment in re.split(r";\s*\n", sql):
                # Drop comment-only / empty fragments.
                body = "\n".join(
                    l for l in fragment.splitlines() if l.strip() and not l.lstrip().startswith("--")
                )
                if body.strip():
                    # exec_driver_sql passes the literal statement straight to the
                    # DBAPI driver — unlike text(), it does NOT interpret ":word"
                    # tokens (e.g. a "12:30" in a venue/name) as bind parameters.
                    conn.exec_driver_sql(body)
            conn.commit()
        logger.info("  ✓ DB write complete for %s", label)
        return True
    except Exception as exc:
        logger.error("  ✗ DB write failed for %s: %s", label, exc)
        return False
    finally:
        engine.dispose()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    # Load .env if python-dotenv is available
    try:
        from dotenv import load_dotenv  # type: ignore
        # ingestion/.env takes precedence, project-root .env is the fallback
        # (the quickstart only creates the root one).
        for env_file in (
            Path(__file__).parent.parent / ".env",
            Path(__file__).parent.parent.parent / ".env",
        ):
            if env_file.exists():
                load_dotenv(env_file)
                logger.debug("Loaded .env from %s", env_file)
    except ImportError:
        pass

    parser = argparse.ArgumentParser(
        description="Scan PDF_WATCH_DIR for new EFI match reports and ingest them"
    )
    parser.add_argument(
        "--dir", dest="watch_dir", type=Path, default=None,
        help="Override PDF_WATCH_DIR environment variable"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Parse PDFs but do not write to the database"
    )
    parser.add_argument(
        "--force", action="store_true",
        help="Re-process all PDFs, ignoring the processed log"
    )
    parser.add_argument(
        "--file", dest="only_file", type=Path, default=None,
        help="Process only this single PDF (must live inside the watch dir)"
    )
    args = parser.parse_args(argv)

    watch_dir: Path = args.watch_dir.resolve() if args.watch_dir else _watch_dir()
    logger.info("Watch directory: %s", watch_dir)

    all_pdfs = _find_pdfs(watch_dir)
    if args.only_file is not None:
        target = args.only_file.resolve()
        all_pdfs = [p for p in all_pdfs if p.resolve() == target]
        if not all_pdfs:
            logger.error("--file %s not found in watch dir", target)
            return 1
    if not all_pdfs:
        logger.info("No PDF files found in %s — nothing to do", watch_dir)
        return 0

    processed = set() if args.force else _load_processed(watch_dir)
    new_pdfs = [p for p in all_pdfs if str(p.resolve()) not in processed]

    if not new_pdfs:
        logger.info("All %d PDF(s) already processed", len(all_pdfs))
        return 0

    logger.info("Found %d new PDF(s) to process (of %d total)", len(new_pdfs), len(all_pdfs))

    success_count = 0
    fail_count = 0

    for pdf_path in new_pdfs:
        ok = _ingest_pdf(pdf_path, dry_run=args.dry_run)
        if ok:
            success_count += 1
            if not args.dry_run:
                _mark_processed(watch_dir, pdf_path)
        else:
            fail_count += 1

    logger.info(
        "Done — %d ingested, %d failed, %d already processed",
        success_count, fail_count, len(all_pdfs) - len(new_pdfs),
    )
    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
