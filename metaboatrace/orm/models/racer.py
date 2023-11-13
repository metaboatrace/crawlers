from datetime import datetime

from sqlalchemy import Column, Date, DateTime, Enum, Integer, String

from ..database import Base


class Racer(Base):
    __tablename__ = "racers"

    registration_number = Column(Integer, primary_key=True)
    last_name = Column(String(255), nullable=False, default="")
    first_name = Column(String(255), nullable=False, default="")
    gender = Column(Enum("male", "female", name="gender_enum"))
    term = Column(Integer)
    birth_date = Column(Date)
    branch_id = Column(Integer)
    birth_prefecture_id = Column(Integer)
    height = Column(Integer)
    status = Column(Enum("active", "retired", name="status_enum"))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
