from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    Integer,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.sql.schema import ForeignKey

from ..database import Base


class Race(Base):
    __tablename__ = "races"

    stadium_tel_code = Column(Integer, ForeignKey("stadiums.tel_code"), primary_key=True)
    date = Column(Date, primary_key=True)
    race_number = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    course_fixed = Column(Boolean, default=False, nullable=False)
    use_stabilizer = Column(Boolean, default=False, nullable=False)
    number_of_laps = Column(Integer, default=3, nullable=False)
    betting_deadline_at = Column(DateTime, nullable=False, index=True)
    canceled = Column(Boolean, default=False, server_default=text("false"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False, onupdate=datetime.utcnow)


class RaceEntry(Base):
    __tablename__ = "race_entries"

    stadium_tel_code = Column(Integer, ForeignKey("stadiums.tel_code"), primary_key=True)
    date = Column(Date, primary_key=True)
    race_number = Column(Integer, primary_key=True)
    racer_registration_number = Column(Integer, nullable=False)
    pit_number = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint(
            "stadium_tel_code",
            "date",
            "race_number",
            "racer_registration_number",
            name="uniq_index_1",
        ),
    )


class RaceRecord(Base):
    __tablename__ = "race_records"

    stadium_tel_code = Column(Integer, ForeignKey("stadiums.tel_code"), primary_key=True)
    date = Column(Date, primary_key=True)
    race_number = Column(Integer, primary_key=True)
    pit_number = Column(Integer, primary_key=True)
    course_number = Column(Integer, nullable=False)
    start_time = Column(Float)
    start_order = Column(Integer)
    race_time = Column(Float)
    arrival = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False, onupdate=datetime.utcnow)


class CircumferenceExhibitionRecord(Base):
    __tablename__ = "circumference_exhibition_records"

    stadium_tel_code = Column(Integer, ForeignKey("stadiums.tel_code"), primary_key=True)
    date = Column(Date, primary_key=True)
    race_number = Column(Integer, primary_key=True)
    pit_number = Column(Integer, primary_key=True)
    exhibition_time = Column(Float, nullable=False)
    exhibition_time_order = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False, onupdate=datetime.utcnow)


class DisqualifiedRaceEntry(Base):
    __tablename__ = "disqualified_race_entries"

    stadium_tel_code = Column(Integer, ForeignKey("stadiums.tel_code"), primary_key=True)
    date = Column(Date, primary_key=True)
    race_number = Column(Integer, primary_key=True)
    pit_number = Column(Integer, primary_key=True)
    disqualification = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False, onupdate=datetime.utcnow)
