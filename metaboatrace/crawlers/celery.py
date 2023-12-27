from celery import Celery
from celery.schedules import crontab

app = Celery(
    "metaboatrace.crawlers",
    broker="redis://localhost:6379/0",
    include=["metaboatrace.crawlers.scheduler"],
)
app.conf.timezone = "UTC"

# note: 可読性からJSTで定義して、設定時はUTCに変更していたが、これだと毎回計算が実行されオーバヘッドになるので静的に定義
# jst = pytz.timezone("Asia/Tokyo")
# event_crawl_jst_time = datetime.now(jst).replace(hour=8, minute=0)
# event_crawl_utc_time = event_crawl_jst_time.astimezone(pytz.utc)
app.conf.beat_schedule = {
    "crawl-events-every-month": {
        "task": "metaboatrace.crawlers.scheduler.schedule_crawl_events_from_monthly_schedule_page",
        "schedule": crontab(hour=23, minute=30, day_of_month=27),
    },
    "crawl-all-race-information-daily": {
        "task": "metaboatrace.crawlers.scheduler.schedule_crawl_all_race_information_for_today",
        "schedule": crontab(hour=23, minute=0),
    },
    "crawl-events-starting-today-daily": {
        "task": "metaboatrace.crawlers.scheduler.schedule_crawl_events_starting_today_for_today",
        "schedule": crontab(hour=23, minute=15),
    },
    "reserve-crawl-tasks-today-daily": {
        "task": "metaboatrace.crawlers.scheduler.reserve_crawl_task_for_races_today",
        "schedule": crontab(hour=23, minute=10),
    },
    "crawl-incomplete-racers-every-5-minutes": {
        "task": "metaboatrace.crawlers.scheduler.enqueue_incomplete_racer_crawling",
        "schedule": crontab(minute="*/5"),
    },
}
