import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker

engine = create_engine(
    os.environ.get(
        "DATABASE_URL",
        "mysql+pymysql://root:password@127.0.0.1:33306/metaboatrace?charset=utf8mb4",
    )
)

Base = declarative_base()

session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)
