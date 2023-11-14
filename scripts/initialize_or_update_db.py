import logging

from metaboatrace.orm.database import Base, engine
from metaboatrace.orm.models import *

logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

Base.metadata.create_all(engine)
