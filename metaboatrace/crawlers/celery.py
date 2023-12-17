from celery import Celery

app = Celery("metaboatrace", broker="redis://localhost:6379/0")
app.conf.timezone = "UTC"

import metaboatrace.crawlers.race
import metaboatrace.crawlers.racer
import metaboatrace.crawlers.stadium
