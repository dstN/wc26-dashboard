from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Computed
from app.models.base import Base


class MatchOfferingStat(Base):
    __tablename__ = "match_offering_stats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=True)
    scope = Column(Enum("match", "team_aggregate"), nullable=False, default="match")
    match_key = Column(Integer, Computed("IFNULL(match_id,0)"), nullable=False)
    total_offers_made = Column(Integer, nullable=True)
    total_offers_received = Column(Integer, nullable=True)
    offers_final_third = Column(Integer, nullable=True)
    offers_middle_third = Column(Integer, nullable=True)
    offers_defensive_third = Column(Integer, nullable=True)
    inside_shape = Column(Integer, nullable=True)
    outside_shape = Column(Integer, nullable=True)
    most_player = Column(String(100), nullable=True)
    most_count = Column(Integer, nullable=True)
