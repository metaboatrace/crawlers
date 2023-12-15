import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker

engine = create_engine(
    os.environ.get(
        "DATABASE_URL",
        "postgresql://postgres:password@127.0.0.1:55432/metaboatrace_development",
    )
)

Base = declarative_base()

session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)
