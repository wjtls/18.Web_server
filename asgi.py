# your_project_name/asgi.py
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack # 웹소켓 연결 시 사용자 인증 처리
import chat.routing # chat 앱의 라우팅 설정 가져오기

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project_name.settings') # 'your_project_name'을 실제 프로젝트 이름으로 변경

application = ProtocolTypeRouter({
  # 표준 HTTP 요청을 처리하는 Django의 ASGI 애플리케이션
  "http": get_asgi_application(),

  # 웹소켓 핸들러
  "websocket": AuthMiddlewareStack( # 웹소켓 연결을 Django 인증 시스템으로 감싸기
        URLRouter(
            chat.routing.websocket_urlpatterns # chat 앱의 라우팅 설정 지정
        )
    ),
})
