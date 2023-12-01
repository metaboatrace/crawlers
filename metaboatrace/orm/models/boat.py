from datetime import datetime

from sqlalchemy import Boolean, Column, Date, DateTime, Float, ForeignKey, Integer, UniqueConstraint

from ..database import Base


class BoatSetting(Base):
    """
    BoatSettingモデルは、レース毎のボート設定情報を管理します。

    注意: もともとは以下のようなユニーク制約を設けていました。
    - boat_number: Integer, nullable=False
    - motor_number: Integer, nullable=False
    - __table_args__: 主キー + ボート番号もしくはモーター番号のユニーク制約

    しかし、このモデルは出走表からボートとモーターの番号を取得、チルトやプロペラ交換は直前情報から取得することを想定しています。
    主キーが特定できている状態で上記をupsertする方が処理がシンプルになるため、上記の制約を外しました。
    """

    __tablename__ = "boat_settings"

    stadium_tel_code = Column(Integer, ForeignKey("stadiums.tel_code"), primary_key=True)
    date = Column(Date, primary_key=True)
    race_number = Column(Integer, primary_key=True)
    pit_number = Column(Integer, primary_key=True)
    boat_number = Column(Integer, nullable=True)
    motor_number = Column(Integer, nullable=True)
    tilt = Column(Float, nullable=True)
    propeller_renewed = Column(Boolean, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


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
