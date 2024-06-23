import argparse
import logging
import os
import subprocess
from datetime import datetime

from metaboatrace.models.racer import EvaluationPeriodType, RacerRatingEvaluationTerm
from sqlalchemy import text

from metaboatrace.orm.database import Session

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://postgres:password@127.0.0.1:55432/metaboatrace_development"
)

BACKUP_DIR = "./bak"

TABLE_DATE_COLUMN_MAP = {
    "boat_betting_contribute_rate_aggregations": "aggregated_on",
    "boat_settings": "date",
    "circumference_exhibition_records": "date",
    "disqualified_race_entries": "date",
    "events": "starts_on",
    "motor_betting_contribute_rate_aggregations": "aggregated_on",
    "motor_maintenances": "date",
    "motor_renewals": "date",
    "odds": "date",
    "payoffs": "date",
    "race_entries": "date",
    "race_records": "date",
    "racer_conditions": "date",
    "racer_winning_rate_aggregations": "aggregated_on",
    "races": "date",
    "start_exhibition_records": "date",
    "weather_conditions": "date",
    "winning_race_entries": "date",
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_args():  # type: ignore
    parser = argparse.ArgumentParser(
        description="Remove data included in specified racer evaluation term."
    )
    parser.add_argument("year", type=int, help="The year of the evaluation term.")
    parser.add_argument(
        "half",
        type=int,
        choices=[1, 2],
        help="The half of the evaluation term (1 for first, 2 for second).",
    )
    return parser.parse_args()


def backup_database(backup_file: str, exclude_tables: bool = False) -> None:  # type: ignore
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

    pg_dump_command = [
        "pg_dump",
        "-h",
        "127.0.0.1",
        "-p",
        "55432",
        "-U",
        "postgres",
        "-d",
        "metaboatrace_development",
        "-n",
        "public",
        "--data-only",
        "-f",
        backup_file,
    ]

    if exclude_tables:
        pg_dump_command.extend(["--exclude-table=stadiums", "--exclude-table=racers"])

    logger.info(f"Backing up database to {backup_file}...")
    result = subprocess.run(pg_dump_command, capture_output=True, text=True)

    if result.returncode != 0:
        logger.error(f"Backup failed: {result.stderr}")
        raise Exception("Backup failed")
    logger.info("Backup completed successfully.")


def delete_data_within_term(session, term_start, term_end) -> None:  # type: ignore
    for table, date_column in TABLE_DATE_COLUMN_MAP.items():
        logger.info(f"Deleting data from {table} within {term_start} to {term_end}...")
        delete_query = text(
            f"DELETE FROM {table} WHERE {date_column} BETWEEN :term_start AND :term_end"
        )
        session.execute(delete_query, {"term_start": term_start, "term_end": term_end})
    session.commit()
    logger.info("Data deletion completed.")


def main() -> None:
    args = parse_args()
    year = args.year
    period_type = EvaluationPeriodType(args.half)
    term = RacerRatingEvaluationTerm(year, period_type)
    term_start, term_end = term.starts_on, term.ends_on

    confirmation = input(
        f"Remove data included between {term_start} and {term_end}. Are you sure? (y/N): "
    )
    if confirmation.lower() != "y":
        logger.info("Aborted by user.")
        return

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    pre_deletion_backup_file = os.path.join(BACKUP_DIR, f"backup_{timestamp}.dump")
    backup_database(pre_deletion_backup_file)

    session = Session()
    try:
        delete_data_within_term(session, term_start, term_end)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        session.rollback()
    finally:
        session.close()


if __name__ == "__main__":
    main()
