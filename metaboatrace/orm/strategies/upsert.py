import os
from typing import Any, Callable, Type

import sqlalchemy.dialects.mysql as mysql
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import Session as SQLAlchemySession


def create_upsert_strategy() -> (
    Callable[[SQLAlchemySession, Type[DeclarativeMeta], list[dict[str, Any]], list[str]], bool]
):
    if os.environ.get("DB", "mysql") == "mysql":
        return _mysql_upsert_strategy
    else:
        raise NotImplementedError


def _mysql_upsert_strategy(
    session: SQLAlchemySession,
    model: Type[DeclarativeMeta],
    values: list[dict[str, Any]],
    on_duplicate_key_update: list[str],
) -> bool:
    upsert_statement = mysql.insert(model).values(values)

    update_dict = {field: upsert_statement.inserted[field] for field in on_duplicate_key_update}

    on_duplicate_key_statement = upsert_statement.on_duplicate_key_update(**update_dict)

    session.execute(on_duplicate_key_statement)
    session.commit()

    return True
