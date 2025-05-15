# chart/asgi.py
import os
import django # django를 임포트
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

# ★★★ 중요: DJANGO_SETTINGS_MODULE 환경 변수 설정 ★★★
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chart.settings')

# ★★★ 중요: Django 앱 로딩 및 설정 초기화 ★★★
# Django 모델이나 설정을 사용하는 다른 모듈(예: chat.routing)을 임포트하기 전에 호출
django.setup()

import chat.routing # chat 앱의 라우팅 설정 임포트

# Django의 기본 HTTP 요청 처리 ASGI 애플리케이션 (django.setup() 이후에 호출)
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            chat.routing.websocket_urlpatterns
        )
    ),
})