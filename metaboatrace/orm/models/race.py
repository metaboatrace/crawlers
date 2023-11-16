from datetime import datetime

from sqlalchemy import Boolean, Column, Date, DateTime, Integer, String, text
from sqlalchemy.orm import relationship
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
