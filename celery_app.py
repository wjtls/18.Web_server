#D:\AI_pycharm\pythonProject\3_AI_LLM_finance\c_web_env\celery_app.py
import os
from celery import Celery
from celery.schedules import crontab  # [추가] crontab을 사용하기 위해 import
import firebase_admin                  # [1. 추가] firebase_admin 임포트
from firebase_admin import credentials   # [2. 추가] credentials 임포트



# Celery 앱 생성
app = Celery('chart')

# ▼▼▼ [핵심] 시간대 설정 추가 ▼▼▼
# Django의 TIME_ZONE 설정을 그대로 사용하도록 설정 (UTC로 자동 변환 방지)
app.conf.enable_utc = False
# Celery가 사용할 시간대를 명시적으로 지정
app.conf.timezone = 'Asia/Seoul'


# [핵심] Django의 settings.py 파일을 찾을 수 있도록 이 라인을 반드시 추가해야 합니다.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chart.settings')


# Celery 앱 생성. 이름은 Django 프로젝트 이름('chart')으로 지정하는 것이 좋습니다.
app = Celery('chart')

# 'django.conf:settings'를 사용하여 Django의 settings.py에서 모든 Celery 설정을 읽어오도록 지시합니다.
# namespace='CELERY'는 settings.py에서 CELERY_ 로 시작하는 모든 변수를 읽어오라는 의미입니다.
app.config_from_object('django.conf:settings', namespace='CELERY')

# 등록된 모든 Django 앱에서 tasks.py 파일을 찾아 작업을 자동으로 로드합니다.
app.autodiscover_tasks()


# ▼▼▼▼▼▼▼▼▼▼▼▼▼▼ 스케줄 설정 추가 ▼▼▼▼▼▼▼▼▼▼▼▼▼▼
app.conf.beat_schedule = {
    # '스케줄_이름': { ... }
    'check-ai-trader-signals-every-minute': {
        'task': 'main.tasks.check_ai_trader_signals', # 실행할 태스크 경로
        'schedule': crontab(minute='*'),              # 매 1분마다 실행
    },

    # 퀴즈알람
    'send-quiz-notification-every-minute': {
        'task': 'main.tasks.send_periodic_quiz_notification', # 방금 만든 작업
        'schedule': crontab(minute='*'),                      # 1분마다 실행
    },
}
# =================================================================