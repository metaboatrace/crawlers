from datetime import datetime

from sqlalchemy import Column, Date, DateTime, Float, Integer, String, text

from ..database import Base


class Racer(Base):
    __tablename__ = "racers"

    registration_number = Column(Integer, primary_key=True)
    last_name = Column(String(255), nullable=False, server_default=text("''"))
    first_name = Column(String(255), nullable=False, server_default=text("''"))
    gender = Column(Integer)
    term = Column(Integer)
    birth_date = Column(Date)
    branch_id = Column(Integer)
    birth_prefecture_id = Column(Integer)
    height = Column(Integer)
    status = Column(Integer)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class RacerCondition(Base):
    __tablename__ = "racer_conditions"

    racer_registration_number = Column(Integer, primary_key=True)
    date = Column(Date, primary_key=True)
    weight = Column(Float, nullable=False)
    adjust = Column(Float, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
