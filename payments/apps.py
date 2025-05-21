# payments/apps.py
from django.apps import AppConfig

class PaymentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'payments' # 앱의 이름입니다. 'payments'가 맞는지 확인하세요.