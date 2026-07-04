from ingestion.slugs import TEAM_SLUGS, SUBPAGES

BASE = "https://efidatareference.com"


def team_page(slug: str) -> str:
    return f"{BASE}/{slug}-2026/"


def team_subpage(slug: str, section_key: str) -> str:
    suffix = SUBPAGES[section_key]
    return f"{BASE}/{slug}-2026-{suffix}/"


def team_urls(slug: str) -> dict[str, str]:
    return {key: team_subpage(slug, key) for key in SUBPAGES}


def all_team_routes() -> list[tuple[str, str, str]]:
    return [
        (slug, key, team_subpage(slug, key))
        for slug in TEAM_SLUGS
        for key in SUBPAGES
    ]
