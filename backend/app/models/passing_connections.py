from sqlalchemy import Column, Integer, Numeric, String, ForeignKey
from app.models.base import Base


class PassingConnection(Base):
    __tablename__ = "passing_connections"

    id = Column(Integer, primary_key=True, autoincrement=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False)
    rank_no = Column(Integer, nullable=False)
    from_name = Column(String(100), nullable=True)
    to_name = Column(String(100), nullable=True)
    pct_of_team_passes = Column(Numeric(5, 2), nullable=True)
