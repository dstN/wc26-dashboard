from sqlalchemy import Column, Integer, Numeric, TIMESTAMP, func
from app.models.base import Base


class TournamentOverview(Base):
    __tablename__ = "tournament_overview"

    id = Column(Integer, primary_key=True, autoincrement=True)
    matches_played = Column(Integer, default=0)
    goals_total = Column(Integer, default=0)
    avg_in_contest_pct = Column(Numeric(5, 2), default=0.00)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
