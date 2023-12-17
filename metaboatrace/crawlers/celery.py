from celery import Celery
from celery.schedules import crontab

from metaboatrace.crawlers.official.website.v1707.stadium import (
    crawl_events_from_monthly_schedule_page,
)

app = Celery("metaboatrace.crawlers", broker="redis://localhost:6379/0")
app.conf.timezone = "UTC"

# HACK: @app.task デコレータを関数定義時に適用することが一般的だが、名前空間パッケージを使ってる兼ね合いからかエラーになるのでここでデコレート
app.task(crawl_events_from_monthly_schedule_page)

# note: 可読性からJSTで定義して、設定時はUTCに変更していたが、これだと毎回計算が実行されオーバヘッドになるので静的に定義
# jst = pytz.timezone("Asia/Tokyo")
# event_crawl_jst_time = datetime.now(jst).replace(hour=7, minute=0)
# event_crawl_utc_time = event_crawl_jst_time.astimezone(pytz.utc)
app.conf.beat_schedule = {
    "crawl-events-every-month": {
        "task": "metaboatrace.crawlers.scheduler.schedule_crawl_events_from_monthly_schedule_page",
        "schedule": crontab(hour=22, minute=0, day_of_month=27),
    }
}
