from sqlalchemy import Column, Computed, Enum, ForeignKey, Integer, Numeric, String

from app.models.base import Base


class DefensiveAction(Base):
    __tablename__ = "defensive_actions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=True)
    scope = Column(Enum("match", "team_aggregate"), nullable=False, default="match")
    match_key = Column(Integer, Computed("IFNULL(match_id,0)"), nullable=False)
    forced_turnovers = Column(Integer, default=0)
    pressure_on_ball = Column(Enum("moderate", "heavy"), default="moderate")
    possession_regained = Column(Integer, nullable=True)
    interceptions = Column(Integer, nullable=True)
    tackles = Column(Integer, nullable=True)
    possession_actions_per_da = Column(Numeric(5, 2), nullable=True)
    blocks_total = Column(Integer, nullable=True)
    blocks_passes = Column(Integer, nullable=True)
    blocks_shots = Column(Integer, nullable=True)
    blocks_crosses = Column(Integer, nullable=True)
    blocks_clearances = Column(Integer, nullable=True)
    contests_total = Column(Integer, nullable=True)
    contests_physical = Column(Integer, nullable=True)
    contests_aerial = Column(Integer, nullable=True)
    contests_duels = Column(Integer, nullable=True)
    most_regains_player = Column(String(100), nullable=True)
    most_regains_count = Column(Integer, nullable=True)
