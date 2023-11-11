from metaboatrace.orm.database import Base, engine

# from metaboatrace.orm.models.racer import Racer

Base.metadata.create_all(engine)
