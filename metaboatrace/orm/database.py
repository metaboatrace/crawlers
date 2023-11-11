import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base

engine = create_engine(
    os.environ.get(
        "DATABASE_URL", "mysql+pymysql://root:password@127.0.0.1:33306/metaboatrace?charset=utf8mb4"
    )
)

Base = declarative_base()
