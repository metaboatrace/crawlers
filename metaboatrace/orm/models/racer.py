from datetime import datetime

from sqlalchemy import Column, Date, DateTime, Integer, String, text

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
