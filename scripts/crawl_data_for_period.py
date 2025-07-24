import argparse
from datetime import datetime, timedelta, date
from time import sleep
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock, Event
import sys

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
# タイムアウトエラー検出用のイベント
timeout_error_event = Event()


def _crawl_single_race(
    stadium_tel_code_value: int, current_date: date, race_number: int, sleep_second: int
) -> dict:
    """単一レースのクロール処理
    
    Returns:
        dict: クロール結果 {"success": bool, "race_number": int, "error": str or None}
    """
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

        return {"success": True, "race_number": race_number, "error": None}

    except RaceCanceled:
        repository = RaceRepository()
        repository.cancel(stadium_tel_code_value, current_date, race_number)
        with print_lock:
            print("\t\t\t\033[90m[info] The race was canceled. Moving to the next event.\033[0m")
        return {"success": False, "race_number": race_number, "error": "canceled"}
    except Exception as e:
        # 予期しないエラーをキャッチして記録
        error_msg = str(e)
        # タイムアウトエラーの場合は特別扱い
        if "timeout" in error_msg.lower() or "timed out" in error_msg.lower():
            with print_lock:
                print(f"\t\t\t\033[91m[CRITICAL] Timeout error detected for race {race_number}!\033[0m")
            timeout_error_event.set()  # タイムアウトエラーを通知
        return {"success": False, "race_number": race_number, "error": error_msg}


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
                        result = _crawl_single_race(
                            e.stadium_tel_code.value, current_date, race_number, sleep_second
                        )
                        if not result["success"] and result["error"] == "canceled":
                            break
                else:
                    # 並列処理（改良版）
                    print(f"\t\tProcessing races 1-12 with {max_workers} workers...")
                    
                    # エラー統計を初期化
                    error_count = 0
                    canceled_count = 0
                    success_count = 0
                    
                    with ThreadPoolExecutor(max_workers=max_workers) as executor:
                        # レース毎のタスクを投入（遅延実行で負荷分散）
                        futures = []
                        for i, race_number in enumerate(race_numbers):
                            # タイムアウトエラーが発生していたら即座に中止
                            if timeout_error_event.is_set():
                                executor.shutdown(wait=False, cancel_futures=True)
                                print(f"\n\033[91m[FATAL] Timeout error detected. Aborting all tasks...\033[0m")
                                error_message = f"💥 FATAL: Timeout error during crawl on {current_date}. Aborted immediately."
                                send_slack_notification(error_message)
                                sys.exit(1)
                            
                            # 各タスクの開始を少しずつ遅延させる
                            if i > 0 and i % max_workers == 0:
                                sleep(sleep_second)
                            
                            future = executor.submit(
                                _crawl_single_race,
                                e.stadium_tel_code.value,
                                current_date,
                                race_number,
                                sleep_second,
                            )
                            futures.append((future, race_number))

                        # 結果を処理
                        for future, race_number in futures:
                            # タイムアウトエラーが発生していたら即座に中止
                            if timeout_error_event.is_set():
                                executor.shutdown(wait=False, cancel_futures=True)
                                print(f"\n\033[91m[FATAL] Timeout error detected. Aborting all tasks...\033[0m")
                                error_message = f"💥 FATAL: Timeout error during crawl on {current_date}. Aborted immediately."
                                send_slack_notification(error_message)
                                sys.exit(1)
                            
                            try:
                                result = future.result(timeout=60)  # 各タスクに60秒のタイムアウトを設定
                                if result["success"]:
                                    success_count += 1
                                    with print_lock:
                                        print(f"\t\t\t✓ Completed {race_number}R")
                                elif result["error"] == "canceled":
                                    canceled_count += 1
                                    with print_lock:
                                        print(f"\t\t\t✗ Race {race_number}R was canceled")
                                else:
                                    error_count += 1
                                    with print_lock:
                                        print(
                                            f"\t\t\t✗ Race {race_number}R failed: {result['error']}"
                                        )
                            except Exception as exc:
                                error_count += 1
                                error_msg = str(exc)
                                with print_lock:
                                    print(
                                        f"\t\t\t✗ Race {race_number}R generated an exception: {exc}"
                                    )
                                # タイムアウトエラーの場合は即座に中止
                                if "timeout" in error_msg.lower():
                                    executor.shutdown(wait=False, cancel_futures=True)
                                    print(f"\n\033[91m[FATAL] Timeout error detected. Aborting all tasks...\033[0m")
                                    error_message = f"💥 FATAL: Timeout error during crawl on {current_date}. Aborted immediately."
                                    send_slack_notification(error_message)
                                    sys.exit(1)
                        
                        # 統計を表示
                        total = len(race_numbers)
                        with print_lock:
                            print(f"\t\t📊 Results: Success={success_count}/{total}, Canceled={canceled_count}, Errors={error_count}")
                        
                        # エラー率が高い場合は警告
                        if error_count > total * 0.3:  # 30%以上のエラー
                            print(f"\t\t⚠️  High error rate detected! Consider reducing parallel workers or increasing sleep time.")

        success_message = f"✅ Successfully completed data crawl from {start_date} to {end_date}"
        send_slack_notification(success_message)

    except Exception as e:
        error_message = f"❌ Error during data crawl from {start_date} to {end_date}: {str(e)}"
        send_slack_notification(error_message)
        raise


if __name__ == "__main__":
    _main()
