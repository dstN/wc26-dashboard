from sqlalchemy import Column, Computed, Enum, ForeignKey, Integer, String

from app.models.base import Base


class CrossStat(Base):
    __tablename__ = "cross_stats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=True)
    scope = Column(Enum("match", "team_aggregate"), nullable=False, default="match")
    match_key = Column(Integer, Computed("IFNULL(match_id,0)"), nullable=False)
    attempted = Column(Integer, nullable=True)
    completed = Column(Integer, nullable=True)
    zone_left = Column(Integer, nullable=True)
    zone_center_left = Column(Integer, nullable=True)
    zone_center_right = Column(Integer, nullable=True)
    zone_right = Column(Integer, nullable=True)
    type_inswing = Column(Integer, nullable=True)
    type_outswing = Column(Integer, nullable=True)
    type_driven = Column(Integer, nullable=True)
    type_lofted = Column(Integer, nullable=True)
    type_cutback = Column(Integer, nullable=True)
    type_push_cross = Column(Integer, nullable=True)
    most_player = Column(String(100), nullable=True)
    most_count = Column(Integer, nullable=True)
