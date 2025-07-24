"""
race_entriesテーブルに存在するがracersテーブルに存在しないレーサーの情報をクロールするスクリプト
"""

import time
from typing import List

from metaboatrace.scrapers.official.website.exceptions import DataNotFound
from sqlalchemy import text
from tqdm import tqdm

from metaboatrace.crawlers.official.website.v1707.racer import crawl_racer_from_racer_profile_page
from metaboatrace.orm.database import Session
from metaboatrace.repositories.racer import RacerRepository


def find_missing_racers() -> List[int]:
    """race_entriesに存在するがracersテーブルに存在しないregistration_numberを取得"""
    session = Session()
    try:
        # race_entriesに存在するがracersに存在しないregistration_numberを取得
        query = text(
            """
            SELECT DISTINCT re.racer_registration_number 
            FROM race_entries re
            LEFT JOIN racers r ON re.racer_registration_number = r.registration_number
            WHERE r.registration_number IS NULL
            ORDER BY re.racer_registration_number
        """
        )

        result = session.execute(query)
        missing_registration_numbers = [row[0] for row in result]

        return missing_registration_numbers
    finally:
        session.close()


def crawl_missing_racers() -> None:
    """存在しないレーサーの情報をクロールして登録"""
    repository = RacerRepository()

    # 存在しないレーサーのregistration_numberを取得
    missing_registration_numbers = find_missing_racers()

    if not missing_registration_numbers:
        print("All racers in race_entries exist in racers table.")
        return

    print(f"Found {len(missing_registration_numbers)} missing racers.")

    # 各レーサーの情報をクロール
    for registration_number in tqdm(missing_registration_numbers, desc="Crawling missing racers"):
        session = Session()
        try:
            # レーサー情報をクロール
            crawl_racer_from_racer_profile_page(registration_number)

            # 負荷軽減のためのスリープ
            if registration_number % 2 == 0:
                time.sleep(1)

            session.commit()
            print(f"\033[92m[success] Successfully crawled racer {registration_number}.\033[0m")
        except DataNotFound:
            # プロフィールページが見つからない場合は引退扱い
            repository.make_retired(registration_number)
            print(
                f"\033[90m[info] Racer {registration_number} marked as retired (DataNotFound).\033[0m"
            )
        except Exception as e:
            print(f"\033[91m[error] Error crawling racer {registration_number}: {e}\033[0m")
            session.rollback()
        finally:
            session.close()

    # 最終確認
    remaining_missing = find_missing_racers()
    if remaining_missing:
        print(
            f"\033[93m[warning] Still {len(remaining_missing)} racers missing after crawling.\033[0m"
        )
    else:
        print("\033[92m[success] All missing racers have been processed.\033[0m")


if __name__ == "__main__":
    crawl_missing_racers()
