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


class BoatBettingContributeRateAggregation(Base):
    __tablename__ = "boat_betting_contribute_rate_aggregations"

    stadium_tel_code = Column(Integer, ForeignKey("stadiums.tel_code"), primary_key=True)
    boat_number = Column(Integer, primary_key=True)
    aggregated_on = Column(Date, primary_key=True)
    quinella_rate = Column(Float, nullable=False)
    trio_rate = Column(Float)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class MotorBettingContributeRateAggregation(Base):
    __tablename__ = "motor_betting_contribute_rate_aggregations"

    stadium_tel_code = Column(Integer, ForeignKey("stadiums.tel_code"), primary_key=True)
    motor_number = Column(Integer, primary_key=True)
    aggregated_on = Column(Date, primary_key=True)
    quinella_rate = Column(Float, nullable=False)
    trio_rate = Column(Float)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class MotorMaintenance(Base):
    __tablename__ = "motor_maintenances"

    stadium_tel_code = Column(Integer, ForeignKey("stadiums.tel_code"), primary_key=True)
    date = Column(Date, primary_key=True)
    race_number = Column(Integer, primary_key=True)
    motor_number = Column(Integer, primary_key=True)
    exchanged_parts = Column(Integer, primary_key=True)
    quantity = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


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
