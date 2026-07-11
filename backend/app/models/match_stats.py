from sqlalchemy import Column, Computed, Enum, ForeignKey, Integer, Numeric

from app.models.base import Base


class MatchStats(Base):
    __tablename__ = "match_stats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=True)
    scope = Column(Enum("match", "team_aggregate"), nullable=False, default="match")
    match_key = Column(Integer, Computed("IFNULL(match_id,0)"), nullable=False)
    possession_team_a = Column(Numeric(5, 2))
    possession_team_b = Column(Numeric(5, 2))
    possession_in_contest = Column(Numeric(5, 2))
    ball_recovery_time_avg = Column(Numeric(5, 2))
    xg_a = Column(Numeric(5, 2))
    xg_b = Column(Numeric(5, 2))
    goals_a = Column(Integer)
    goals_b = Column(Integer)
    shots_total = Column(Integer, nullable=True)
    shots_on_target = Column(Integer, nullable=True)
