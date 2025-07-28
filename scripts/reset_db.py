#!/usr/bin/env python
import logging
import sys

from metaboatrace.orm.database import Base, engine
from metaboatrace.orm.models import *

logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)


def reset_database():
    """Drop all tables and recreate them."""
    print("⚠️  WARNING: This will drop all tables and recreate them.")
    print("All data will be lost!")
    
    response = input("\nAre you sure you want to reset the database? (yes/no): ")
    if response.lower() != "yes":
        print("Database reset cancelled.")
        sys.exit(0)
    
    print("\nDropping all tables...")
    Base.metadata.drop_all(engine)
    
    print("Creating all tables...")
    Base.metadata.create_all(engine)
    
    print("✅ Database reset complete!")
    print("\nNext steps:")
    print("1. Run: uv run python scripts/initialize_master_data.py")
    print("2. Import any necessary data dumps")


if __name__ == "__main__":
    reset_database()