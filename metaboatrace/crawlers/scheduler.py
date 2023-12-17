from datetime import datetime

from metaboatrace.crawlers.celery import app
from metaboatrace.crawlers.official.website.v1707 import crawl_events_from_monthly_schedule_page


@app.task
def schedule_crawl_events_from_monthly_schedule_page() -> None:
    now = datetime.now()
    year = now.year
    month = now.month
    crawl_events_from_monthly_schedule_page(year, month)
