from sqlalchemy import Column, Computed, Enum, ForeignKey, Integer

from app.models.base import Base


class LineBreak(Base):
    __tablename__ = "line_breaks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=True)
    scope = Column(Enum("match", "team_aggregate"), nullable=False, default="match")
    match_key = Column(Integer, Computed("IFNULL(match_id,0)"), nullable=False)
    line_type = Column(Enum("defensive", "midfield", "attacking"), nullable=False)
    attempted = Column(Integer, default=0)
    completed = Column(Integer, default=0)
