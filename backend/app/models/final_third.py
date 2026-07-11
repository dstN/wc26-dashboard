from sqlalchemy import Column, Computed, Enum, ForeignKey, Integer

from app.models.base import Base


class FinalThirdEntry(Base):
    __tablename__ = "final_third_entries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=True)
    scope = Column(Enum("match", "team_aggregate"), nullable=False, default="match")
    match_key = Column(Integer, Computed("IFNULL(match_id,0)"), nullable=False)
    zone = Column(Enum("left", "left_inside", "central", "right_inside", "right"), nullable=False)
    entry_count = Column(Integer, default=0)
