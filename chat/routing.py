from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # ws://서버주소/ws/chat/ 경로로 오는 WebSocket 요청을 ChatConsumer가 처리
    re_path(r'ws/chat/$', consumers.ChatConsumer.as_asgi()),
]