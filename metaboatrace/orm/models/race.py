from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    Index,
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
    title = Column(String(255), nullable=True)  # 中止の時を考慮してNULL許容
    is_course_fixed = Column(Boolean, default=False, nullable=False)
    is_stabilizer_used = Column(Boolean, default=False, nullable=False)
    number_of_laps = Column(Integer, default=3, nullable=False)
    betting_deadline_at = Column(DateTime, nullable=True)  # 中止の時を考慮してNULL許容
    is_canceled = Column(Boolean, default=False, server_default=text("false"), nullable=False)
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
        Index("idx_race_entries_date_racer", "date", "racer_registration_number"),
        Index("idx_race_entries_racer_date", "racer_registration_number", "date"),
        Index(
            "idx_race_entries_racer_stadium_date",
            "racer_registration_number",
            "stadium_tel_code",
            "date",
            "race_number",
        ),
        Index(
            "idx_race_entries_date_stadium_multi",
            "date",
            "stadium_tel_code",
            "racer_registration_number",
            postgresql_include=["race_number", "pit_number"],
        ),
    )


class StartExhibitionRecord(Base):
    __tablename__ = "start_exhibition_records"

    stadium_tel_code = Column(Integer, ForeignKey("stadiums.tel_code"), primary_key=True)
    date = Column(Date, primary_key=True)
    race_number = Column(Integer, primary_key=True)
    pit_number = Column(Integer, primary_key=True)
    course_number = Column(Integer, nullable=False)
    start_time = Column(Float, nullable=False)  # note: 展示での出遅れは1で記録
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False, onupdate=datetime.utcnow)


class CircumferenceExhibitionRecord(Base):
    __tablename__ = "circumference_exhibition_records"

    stadium_tel_code = Column(Integer, ForeignKey("stadiums.tel_code"), primary_key=True)
    date = Column(Date, primary_key=True)
    race_number = Column(Integer, primary_key=True)
    pit_number = Column(Integer, primary_key=True)
    exhibition_time = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False, onupdate=datetime.utcnow)


class RaceRecord(Base):
    __tablename__ = "race_records"

    stadium_tel_code = Column(Integer, ForeignKey("stadiums.tel_code"), primary_key=True)
    date = Column(Date, primary_key=True, index=True)
    race_number = Column(Integer, primary_key=True)
    pit_number = Column(Integer, primary_key=True)
    course_number = Column(Integer, nullable=False, index=True)
    start_time = Column(Float)
    race_time = Column(Float)
    arrival = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False, onupdate=datetime.utcnow)

    __table_args__ = (
        Index(
            "idx_race_records_start_time_not_null",
            "stadium_tel_code",
            "date",
            "race_number",
            "pit_number",
            postgresql_where=text("start_time IS NOT NULL"),
        ),
    )


class WinningRaceEntry(Base):
    __tablename__ = "winning_race_entries"

    stadium_tel_code = Column(Integer, ForeignKey("stadiums.tel_code"), primary_key=True)
    date = Column(Date, primary_key=True)
    race_number = Column(Integer, primary_key=True)
    pit_number = Column(Integer, primary_key=True)
    winning_trick = Column(Integer, nullable=False, index=True)
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


class Odds(Base):
    __tablename__ = "odds"

    stadium_tel_code = Column(Integer, ForeignKey("stadiums.tel_code"), primary_key=True)
    date = Column(Date, primary_key=True)
    race_number = Column(Integer, primary_key=True)
    betting_method = Column(Integer, primary_key=True)
    betting_number = Column(Integer, primary_key=True)
    ratio = Column(Float, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("idx_odds_date_stadium_race", "date", "stadium_tel_code", "race_number"),
    )


# NOTE:
#
# Odds モデルと構造が似通っているので統一できると設計初期段階では考えていた
# （このテーブルで持ちたいのは払戻し金額だから、odds に当選カラムみたいなの作るか正規化するならhas_one関連でテーブル先にひとつ作るかすればいいと考えていた）
# ただし、ドメインロジック上払戻金は必ずしもオッズの比率と一致するとは言えないため、このようなテーブルで別途保持する必要があると考えた
# 例えば、艇番123、三連単オッズ10倍 で決まったレースでも4号艇がフライングしてたら返還が発生するので、購入時のオッズである10倍（¥1,000）の払戻しではなくなる
class Payoff(Base):
    __tablename__ = "payoffs"

    stadium_tel_code = Column(Integer, ForeignKey("stadiums.tel_code"), primary_key=True)
    date = Column(Date, primary_key=True)
    race_number = Column(Integer, primary_key=True)
    betting_method = Column(Integer, primary_key=True)
    betting_number = Column(Integer, primary_key=True)
    amount = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
