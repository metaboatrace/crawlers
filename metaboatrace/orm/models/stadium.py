from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, Column, Date, DateTime, Float, Integer, String, text
from sqlalchemy.sql.schema import ForeignKey

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


class Event(Base):
    __tablename__ = "events"

    # hack: title を主キーはバグの温床
    #
    # タイトルが一文字でも違っていたら（例えば公式サイトのクロールを何回かかけたときにタイトルが更新されていたら）データが重複して冪等性が担保できなくなる
    # かといってGPやCCみたいなダブル開催は [:stadium_tel_code, :starts_on] だけだと保持できないからすぐには解決策が浮かばない

    stadium_tel_code = Column(Integer, ForeignKey("stadiums.tel_code"), primary_key=True)
    starts_on = Column(Date, primary_key=True)
    title = Column(String(255), primary_key=True)
    grade = Column(Integer, nullable=False)
    kind = Column(Integer, nullable=False)
    canceled = Column(Boolean, server_default=text("false"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False, onupdate=datetime.utcnow)


class WeatherCondition(Base):
    __tablename__ = "weather_conditions"

    stadium_tel_code = Column(Integer, ForeignKey("stadiums.tel_code"), primary_key=True)
    date = Column(Date, primary_key=True)
    race_number = Column(Integer, primary_key=True)
    in_performance = Column(Boolean, primary_key=True)
    weather = Column(Integer, nullable=False)
    wind_velocity = Column(Float, nullable=False)
    wind_angle = Column(Float)
    wavelength = Column(Float)
    air_temperature = Column(Float, nullable=False)
    water_temperature = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False, onupdate=datetime.utcnow)


class MotorRenewal(Base):
    __tablename__ = "motor_renewals"

    stadium_tel_code = Column(Integer, ForeignKey("stadiums.tel_code"), primary_key=True)
    date = Column(Date, primary_key=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
