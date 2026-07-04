#!/usr/bin/env python
"""CLI entry point for the EFI ingestion pipeline.

Usage:
    python -m ingestion.run --all
    python -m ingestion.run --team germany --match-id 10
    python -m ingestion.run --all --dry-run
"""
import argparse
import asyncio
import logging
import os
import sys

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from ingestion.clean import clean
from ingestion.extract import extract
from ingestion.mapping import slug_for_name, team_id_for_slug
from ingestion.routing import team_urls, all_team_routes
from ingestion.slugs import TEAM_SLUGS
import ingestion.load as loader

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("ingestion.run")

_SUBPAGE_LOADERS = {
    "phases": loader.upsert_phases,
    "line-breaks": loader.upsert_line_breaks,
    "spatial": loader.upsert_spatial,
    "final-third": loader.upsert_final_third,
    "defensive": loader.upsert_defensive,
}


def _db_url() -> str:
    user = os.environ.get("MYSQL_USER", "efi")
    pw = os.environ.get("MYSQL_PASSWORD", "efi")
    host = os.environ.get("MYSQL_HOST", "db")
    port = os.environ.get("MYSQL_PORT", "3306")
    db = os.environ.get("MYSQL_DATABASE", "wc26")
    return f"mysql+asyncmy://{user}:{pw}@{host}:{port}/{db}"


async def ingest_team(
    session: AsyncSession,
    slug: str,
    slug_to_id: dict[str, int],
    match_id: int | None,
    dry_run: bool,
) -> None:
    urls = team_urls(slug)
    team_id = team_id_for_slug(slug, slug_to_id)
    if team_id is None:
        logger.warning("No team_id for slug %r — skipping", slug)
        return

    scope = "match" if match_id else "team_aggregate"

    # General stats (match_stats table)
    df = await extract(urls["general"], "general")
    if df is not None:
        df = clean(df)
        if not dry_run:
            affected = await loader.upsert_team_stats(session, df, team_id, match_id, scope)
            logger.info("%s general: %d rows upserted", slug, affected)
        else:
            logger.info("[dry-run] %s general: %d rows", slug, len(df))

    # All other subpages
    for subpage, load_fn in _SUBPAGE_LOADERS.items():
        df = await extract(urls[subpage], subpage)
        if df is None:
            continue
        df = clean(df)
        if not dry_run:
            affected = await load_fn(session, df, team_id, match_id)
            logger.info("%s %s: %d rows upserted", slug, subpage, affected)
        else:
            logger.info("[dry-run] %s %s: %d rows", slug, subpage, len(df))


async def _load_slug_to_id(session: AsyncSession) -> dict[str, int]:
    from sqlalchemy import text
    result = await session.execute(text("SELECT team_id, team_slug FROM teams"))
    return {row.team_slug: row.team_id for row in result}


async def main(args: argparse.Namespace) -> None:
    engine = create_async_engine(_db_url(), echo=False)
    Session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with Session() as session:
        slug_to_id = await _load_slug_to_id(session)

        if args.all:
            slugs = TEAM_SLUGS
        elif args.team:
            slugs = [args.team]
        else:
            logger.error("Specify --all or --team <slug>")
            sys.exit(1)

        for slug in slugs:
            logger.info("Ingesting %s …", slug)
            async with session.begin():
                await ingest_team(
                    session,
                    slug,
                    slug_to_id,
                    match_id=args.match_id,
                    dry_run=args.dry_run,
                )

    await engine.dispose()
    logger.info("Done.")


def cli() -> None:
    parser = argparse.ArgumentParser(description="EFI WC26 data ingestion")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--all", action="store_true", help="Ingest all 48 teams")
    group.add_argument("--team", metavar="SLUG", help="Ingest a single team slug")
    parser.add_argument("--match-id", type=int, default=None, help="Match ID (omit for aggregate)")
    parser.add_argument("--dry-run", action="store_true", help="Parse but don't write to DB")
    args = parser.parse_args()
    asyncio.run(main(args))


if __name__ == "__main__":
    cli()
