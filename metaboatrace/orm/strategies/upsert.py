import os
from typing import Any, Callable, Type

import sqlalchemy.dialects.mysql as mysql
import sqlalchemy.dialects.postgresql as postgresql
from sqlalchemy import inspect
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import Session as SQLAlchemySession


def create_upsert_strategy() -> Callable[
    [
        SQLAlchemySession,
        Type[DeclarativeMeta],
        list[dict[str, Any]],
        list[str],
    ],
    bool,
]:
    if os.environ.get("DB", "postgresql") == "mysql":
        return _mysql_upsert_strategy
    else:
        return _postgresql_upsert_strategy


def _mysql_upsert_strategy(
    session: SQLAlchemySession,
    model: Type[DeclarativeMeta],
    values: list[dict[str, Any]],
    on_duplicate_key_update: list[str],
) -> bool:
    try:
        upsert_statement = mysql.insert(model).values(values)
        update_dict = {field: upsert_statement.inserted[field] for field in on_duplicate_key_update}
        on_duplicate_key_statement = upsert_statement.on_duplicate_key_update(**update_dict)
        session.execute(on_duplicate_key_statement)
        session.commit()

        return True
    except Exception as e:
        session.rollback()
        raise e


def _postgresql_upsert_strategy(
    session: SQLAlchemySession,
    model: Type[DeclarativeMeta],
    values: list[dict[str, Any]],
    on_duplicate_key_update: list[str],
) -> bool:
    try:
        index_elements = _get_primary_keys(model)
        for value in values:
            upsert_statement = postgresql.insert(model).values(value)
            update_dict = {
                field: upsert_statement.excluded[field] for field in on_duplicate_key_update
            }
            on_conflict_statement = upsert_statement.on_conflict_do_update(
                index_elements=index_elements, set_=update_dict
            )
            session.execute(on_conflict_statement)
        session.commit()

        return True
    except Exception as e:
        session.rollback()
        raise e


def _get_primary_keys(model: Type[DeclarativeMeta]) -> list[str]:
    """
    指定された SQLAlchemy モデルから主キーのカラム名のリストを返す。
    :param model: SQLAlchemy モデルクラス
    :return: 主キーのカラム名のリスト
    """
    mapper = inspect(model)
    if mapper is None:
        raise ValueError("Model has no mapper or is not a valid SQLAlchemy model.")
    return [key.name for key in mapper.primary_key]
