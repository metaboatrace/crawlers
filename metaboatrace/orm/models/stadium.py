from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String

from ..database import Base


class WaterQuality(Enum):
    fresh = 1
    brackish = 2
    sea = 3


class Stadium(Base):
    __tablename__ = "stadiums"

    tel_code = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    prefecture_id = Column(Integer, nullable=False)
    water_quality = Column(Integer, nullable=False)
    tide_fluctuation = Column(Boolean, nullable=False)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    elevation = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False, onupdate=datetime.utcnow)
