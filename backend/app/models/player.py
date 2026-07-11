from sqlalchemy import Column, ForeignKey, Integer, String

from app.models.base import Base


class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, autoincrement=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    name = Column(String(100), nullable=False)
    position = Column(String(50))
    jersey_number = Column(Integer)
