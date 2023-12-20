import argparse
from datetime import datetime, timedelta
from time import sleep

from metaboatrace.models.stadium import EventHoldingStatus
from metaboatrace.scrapers.official.website.exceptions import DataNotFound, RaceCanceled
from tqdm import tqdm

from metaboatrace.crawlers.official.website.v1707.race import (
    crawl_race_before_information_page,
    crawl_race_information_page,
    crawl_race_result_page,
    crawl_trifecta_odds_page,
)
from metaboatrace.crawlers.official.website.v1707.stadium import (
    crawl_event_holding_page,
    crawl_events_from_monthly_schedule_page,
    crawl_pre_inspection_information_page,
)


def _valid_end_date(s: str) -> datetime.date:
    try:
        end_date = datetime.strptime(s, "%Y-%m-%d").date()
        if end_date >= datetime.now().date():
            raise argparse.ArgumentTypeError("end_date は本日以前の日付である必要があります。")
        return end_date
    except ValueError:
        raise argparse.ArgumentTypeError("不正な日付形式です。YYYY-MM-DD 形式で入力してください。")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="クロールする期間を指定してデータを取得します。")
    parser.add_argument(
        "start_date",
        type=lambda s: datetime.strptime(s, "%Y-%m-%d").date(),
        help="開始日 (YYYY-MM-DD 形式)",
    )
    parser.add_argument("end_date", type=_valid_end_date, help="終了日 (YYYY-MM-DD 形式)")
    parser.add_argument("--sleep", type=int, default=1, help="クロール間のスリープ時間 (秒)")
    return parser.parse_args()


def _main() -> None:
    args = _parse_args()
    start_date = args.start_date
    end_date = args.end_date
    sleep_second = args.sleep

    total_days = (end_date - start_date).days + 1

    for day_offset in tqdm(range(total_days), desc="Processing", unit="day"):
        current_date = start_date + timedelta(days=day_offset)
        print(current_date.strftime("%Y-%m-%d"))

        if current_date.day == 1:
            crawl_events_from_monthly_schedule_page(current_date.year, current_date.month)
            print("\tProcessing monthly schedule page.")
            sleep(sleep_second)

        event_holdings = crawl_event_holding_page(current_date)
        will_be_opned_event_holdings = [
            e for e in event_holdings if e.status == EventHoldingStatus.OPEN
        ]
        for e in will_be_opned_event_holdings:
            print(f"\t{e.stadium_tel_code.name} day {e.progress_day}")
            if e.progress_day == 1:
                try:
                    crawl_pre_inspection_information_page(e.stadium_tel_code.value, current_date)
                    print("\t\tProcessing pre inspection information page.")
                    sleep(sleep_second)
                except DataNotFound:
                    print(
                        "\t\t\t\033[93m[warn] The pre inspection information page had not found.\033[0m"
                    )

            for race_number in range(1, 13):
                print(f"\t\tProcessing {race_number}R pages.")
                try:
                    crawl_functions = [
                        crawl_race_information_page,
                        crawl_race_before_information_page,
                        crawl_race_result_page,
                        crawl_trifecta_odds_page,
                    ]

                    for crawl_function in crawl_functions:
                        crawl_function(e.stadium_tel_code.value, current_date, race_number)
                        sleep(sleep_second)
                except RaceCanceled:
                    print("\t\t\t\033[91merror: The race had canceled.\033[0m")


if __name__ == "__main__":
    _main()
