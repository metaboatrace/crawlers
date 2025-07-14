import argparse
from datetime import datetime, timedelta, date
from time import sleep
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

from metaboatrace.models.stadium import EventHoldingStatus
from metaboatrace.scrapers.official.website.exceptions import DataNotFound, RaceCanceled
from tqdm import tqdm

from metaboatrace.crawlers.exceptions import IncompleteDataError, RaceDeadlineChanged
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
from metaboatrace.repositories import RaceRepository
from metaboatrace.crawlers.utils import send_slack_notification


def _valid_end_date(s: str) -> date:
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
    parser.add_argument("--parallel", type=int, default=1, help="並列実行数 (デフォルト: 1)")
    return parser.parse_args()


# 進捗表示用のロック
print_lock = Lock()


def _crawl_single_race(
    stadium_tel_code_value: int, current_date: date, race_number: int, sleep_second: int
) -> None:
    """単一レースのクロール処理"""
    try:
        crawl_functions = [
            crawl_race_information_page,
            crawl_race_before_information_page,
            crawl_race_result_page,
            crawl_trifecta_odds_page,
        ]

        for crawl_function in crawl_functions:
            try:
                crawl_function(stadium_tel_code_value, current_date, race_number)
            except IncompleteDataError:
                with print_lock:
                    print(
                        f"\t\t\t\033[94m[notice] Partial data missing in {crawl_function.__name__}. Continuing with next task.\033[0m"
                    )
            except RaceDeadlineChanged:
                pass

            sleep(sleep_second)

    except RaceCanceled:
        repository = RaceRepository()
        repository.cancel(stadium_tel_code_value, current_date, race_number)
        with print_lock:
            print("\t\t\t\033[90m[info] The race was canceled. Moving to the next event.\033[0m")
        raise  # 上位で処理するために再発生


def _main() -> None:
    args = _parse_args()
    start_date = args.start_date
    end_date = args.end_date
    sleep_second = args.sleep
    max_workers = args.parallel

    start_message = f"🚀 Starting data crawl from {start_date} to {end_date}"
    send_slack_notification(start_message)

    try:
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
                        crawl_pre_inspection_information_page(
                            e.stadium_tel_code.value, current_date
                        )
                        print("\t\tProcessing pre inspection information page.")
                        sleep(sleep_second)
                    except DataNotFound:
                        print(
                            "\t\t\t\033[93m[warn] The pre inspection information page had not found.\033[0m"
                        )

                race_numbers = list(range(1, 13))

                if max_workers == 1:
                    # シリアル処理（従来通り）
                    for race_number in race_numbers:
                        print(f"\t\tProcessing {race_number}R pages.")
                        try:
                            _crawl_single_race(
                                e.stadium_tel_code.value, current_date, race_number, sleep_second
                            )
                        except RaceCanceled:
                            break
                else:
                    # 並列処理
                    print(f"\t\tProcessing races 1-12 with {max_workers} workers...")
                    with ThreadPoolExecutor(max_workers=max_workers) as executor:
                        # レース毎のタスクを投入
                        future_to_race = {
                            executor.submit(
                                _crawl_single_race,
                                e.stadium_tel_code.value,
                                current_date,
                                race_number,
                                sleep_second,
                            ): race_number
                            for race_number in race_numbers
                        }

                        # 結果を処理
                        for future in as_completed(future_to_race):
                            race_number = future_to_race[future]
                            try:
                                future.result()
                                with print_lock:
                                    print(f"\t\t\t✓ Completed {race_number}R")
                            except RaceCanceled:
                                with print_lock:
                                    print(f"\t\t\t✗ Race {race_number}R was canceled")
                                # 並列処理では個別のキャンセルは継続
                            except Exception as exc:
                                with print_lock:
                                    print(
                                        f"\t\t\t✗ Race {race_number}R generated an exception: {exc}"
                                    )

        success_message = f"✅ Successfully completed data crawl from {start_date} to {end_date}"
        send_slack_notification(success_message)

    except Exception as e:
        error_message = f"❌ Error during data crawl from {start_date} to {end_date}: {str(e)}"
        send_slack_notification(error_message)
        raise


if __name__ == "__main__":
    _main()
