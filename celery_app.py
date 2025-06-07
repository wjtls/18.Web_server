# 자동스케줄러( 앱 알람용)

import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'c_web_env.settings')

app = Celery('c_web_env')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Celery Beat 스케줄 설정
app.conf.beat_schedule = {
    'check-ai-trader-signals-every-minute': {
        'task': 'main.tasks.check_ai_trader_signals', # 실행할 태스크 경로
        'schedule': crontab(minute='*'),  # 매 1분마다 실행
    },
}