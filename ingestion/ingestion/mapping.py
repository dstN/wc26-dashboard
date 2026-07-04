"""Map extracted team names to DB team IDs via fuzzy slug matching."""
import re
from typing import Optional

from ingestion.slugs import TEAM_SLUGS


def _slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower().strip()).strip("-")


def _best_match(slug: str, candidates: list[str]) -> Optional[str]:
    if slug in candidates:
        return slug
    # prefix match
    matches = [c for c in candidates if c.startswith(slug[:4])]
    return matches[0] if len(matches) == 1 else None


def slug_for_name(team_name: str) -> Optional[str]:
    slug = _slugify(team_name)
    return _best_match(slug, TEAM_SLUGS)


# Explicit overrides for names that differ from slugs
_OVERRIDES: dict[str, int] = {
    "germany": 1,
    "curacao": 2,
}


def team_id_for_slug(slug: str, slug_to_id: dict[str, int]) -> Optional[int]:
    return _OVERRIDES.get(slug) or slug_to_id.get(slug)
