import os
from datetime import timedelta

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main.settings")

app = Celery("main")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.conf.beat_schedule = {
    "hot_deals_task": {
        "task": "products.tasks.hot_deals_task",
        "schedule": timedelta(seconds=60*60),
    #"options": {"queue": "hot_deals_queue"},
    },
}
app.autodiscover_tasks()