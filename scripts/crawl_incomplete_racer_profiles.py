import time

from tqdm import tqdm

from metaboatrace.crawlers.official.website.v1707.racer import crawl_racer_from_racer_profile_page
from metaboatrace.orm.database import Session
from metaboatrace.orm.models.racer import Racer
from metaboatrace.repositories.racer import RacerRepository
from metaboatrace.scrapers.official.website.exceptions import DataNotFound


def update_racers() -> None:
    repository = RacerRepository()
    try:
        all_racers = Session()
        racers = all_racers.query(Racer).filter(Racer.status.is_(None)).all()
        all_racers.close()

        for racer in tqdm(racers, desc="Updating racers"):
            session = Session()
            try:
                crawl_racer_from_racer_profile_page(int(racer.registration_number))
                if racer.registration_number % 3 == 0:
                    time.sleep(1)
                session.commit()
                print(
                    f"\033[92m[success] Successfully processed racer {racer.registration_number}.\033[0m"
                )
            except DataNotFound:
                repository.make_retired(racer.registration_number)
                print(
                    f"\033[90m[info] Racer {racer.registration_number} retired due to DataNotFound.\033[0m"
                )
            except Exception as e:
                print(
                    f"\033[91m[error] Error processing racer {racer.registration_number}: {e}\033[0m"
                )
                session.rollback()
            finally:
                session.close()
    except Exception as e:
        print(f"\033[91m[error] Error retrieving racers: {e}\033[0m")


if __name__ == "__main__":
    update_racers()
