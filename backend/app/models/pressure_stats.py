from sqlalchemy import Column, Integer, Numeric, String, ForeignKey, Enum, Computed
from app.models.base import Base


class MatchPressureStat(Base):
    __tablename__ = "match_pressure_stats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=True)
    scope = Column(Enum("match", "team_aggregate"), nullable=False, default="match")
    match_key = Column(Integer, Computed("IFNULL(match_id,0)"), nullable=False)
    total_pressures = Column(Integer, nullable=True)
    direct_pressures = Column(Integer, nullable=True)
    avg_duration_s = Column(Numeric(5, 2), nullable=True)
    forced_turnovers = Column(Integer, nullable=True)
    ball_recovery_time_s = Column(Numeric(5, 2), nullable=True)
    pushing_on_into_pressing = Column(Integer, nullable=True)
    pushing_on = Column(Integer, nullable=True)
    direction_inside = Column(Integer, nullable=True)
    direction_outside = Column(Integer, nullable=True)
    most_direct_player = Column(String(100), nullable=True)
    most_direct_count = Column(Integer, nullable=True)
