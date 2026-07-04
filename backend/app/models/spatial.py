from sqlalchemy import Column, Integer, Numeric, ForeignKey, Enum, Computed
from app.models.base import Base


class TeamSpatialStat(Base):
    __tablename__ = "team_spatial_stats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=True)
    scope = Column(Enum("match", "team_aggregate"), nullable=False, default="match")
    match_key = Column(Integer, Computed("IFNULL(match_id,0)"), nullable=False)
    block_type = Column(
        Enum("high", "mid", "low", "build_up_low", "build_up_mid", "final_third_phase"),
        nullable=False, default="mid"
    )
    defensive_line_height = Column(Numeric(5, 2))
    team_length = Column(Numeric(5, 2))
    width_m = Column(Numeric(5, 2), nullable=True)
