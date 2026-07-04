from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, Enum, Computed
from app.models.base import Base


class MatchPhase(Base):
    __tablename__ = "match_phases"

    id = Column(Integer, primary_key=True, autoincrement=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=True)
    scope = Column(Enum("match", "team_aggregate"), nullable=False, default="match")
    match_key = Column(Integer, Computed("IFNULL(match_id,0)"), nullable=False)
    phase_name = Column(String(100), nullable=False)
    phase_group = Column(Enum("in", "out"), nullable=False)
    pct = Column(Numeric(5, 2))
