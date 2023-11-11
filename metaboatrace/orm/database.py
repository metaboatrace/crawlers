import os

from sqlalchemy import create_engine

engine = create_engine(
    os.environ.get(
        "DATABASE_URL", "mysql+pymysql://root:password@127.0.0.1/metaboatrace?charset=utf8mb4"
    )
)
