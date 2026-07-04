from sqlalchemy import Column, Integer, ForeignKey, Enum, Computed
from app.models.base import Base


class MatchSetPlayStat(Base):
    __tablename__ = "match_set_play_stats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=True)
    scope = Column(Enum("match", "team_aggregate"), nullable=False, default="match")
    match_key = Column(Integer, Computed("IFNULL(match_id,0)"), nullable=False)
    set_plays = Column(Integer, nullable=True)
    free_kicks = Column(Integer, nullable=True)
    free_kicks_direct = Column(Integer, nullable=True)
    free_kicks_indirect = Column(Integer, nullable=True)
    penalties = Column(Integer, nullable=True)
    corners = Column(Integer, nullable=True)
    throw_ins = Column(Integer, nullable=True)
    corner_direct_area_left = Column(Integer, nullable=True)
    corner_direct_area_right = Column(Integer, nullable=True)
    corner_direct_area_total = Column(Integer, nullable=True)
    corner_short_left = Column(Integer, nullable=True)
    corner_short_right = Column(Integer, nullable=True)
    corner_short_total = Column(Integer, nullable=True)
    corner_edge_left = Column(Integer, nullable=True)
    corner_edge_right = Column(Integer, nullable=True)
    corner_edge_total = Column(Integer, nullable=True)
    corner_inswing = Column(Integer, nullable=True)
    corner_outswing = Column(Integer, nullable=True)
    corner_driven = Column(Integer, nullable=True)
    corner_lofted = Column(Integer, nullable=True)
