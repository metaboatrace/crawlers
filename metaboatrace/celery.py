from celery import Celery

app = Celery("metaboatrace", broker="redis://localhost:6379/0")
