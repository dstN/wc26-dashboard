"""
Shared tournament-stage filter for stats endpoints.

matches.group_letter is 'A'-'L' (single char) for the group stage, or one of
R32/R16/QF/SF/3RD/FIN (2-3 chars) for knockout rounds — see
ingestion/pmsr_to_sql.py. Using char length instead of an explicit letter
list means new group letters need no changes here.
"""

from typing import Literal, Optional

from sqlalchemy import func
from sqlalchemy.sql.elements import ColumnElement

from app.models import Match

Stage = Literal["group", "knockout"]


def stage_condition(stage: Optional[Stage]) -> Optional[ColumnElement]:
    """Return a filter condition on Match.group_letter, or None for no filter."""
    if stage == "group":
        return func.char_length(Match.group_letter) == 1
    if stage == "knockout":
        return func.char_length(Match.group_letter) > 1
    return None
