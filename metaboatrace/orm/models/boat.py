from datetime import datetime

from sqlalchemy import Boolean, Column, Date, DateTime, Float, ForeignKey, Integer, UniqueConstraint

from ..database import Base


class BoatSetting(Base):
    __tablename__ = "boat_settings"

    stadium_tel_code = Column(Integer, ForeignKey("stadiums.tel_code"), primary_key=True)
    date = Column(Date, primary_key=True)
    race_number = Column(Integer, primary_key=True)
    pit_number = Column(Integer, primary_key=True)
    boat_number = Column(Integer, nullable=False)
    motor_number = Column(Integer, nullable=False)
    tilt = Column(Float, nullable=False)
    propeller_renewed = Column(Boolean, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint(
            "stadium_tel_code", "date", "race_number", "boat_number", name="uniq_index_1"
        ),
        UniqueConstraint(
            "stadium_tel_code", "date", "race_number", "motor_number", name="uniq_index_2"
        ),
    )


class MotorBettingContributeRateAggregation(Base):
    __tablename__ = "motor_betting_contribute_rate_aggregations"

    stadium_tel_code = Column(Integer, ForeignKey("stadiums.tel_code"), primary_key=True)
    motor_number = Column(Integer, primary_key=True)
    aggregated_on = Column(Date, primary_key=True)
    quinella_rate = Column(Float, nullable=False)
    trio_rate = Column(Float)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
