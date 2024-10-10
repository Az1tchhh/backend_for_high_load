from django.conf import settings
import os

from celery import Celery

from config.settings import CELERY_BROKER_URL

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config', broker=CELERY_BROKER_URL, backend=CELERY_BROKER_URL)

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks(settings.INSTALLED_APPS)
app.conf.timezone = 'Asia/Almaty'
app.conf.broker_url = CELERY_BROKER_URL
app.conf.broker_connection_retry_on_startup = True
