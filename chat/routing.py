# chat/routing.py
from django.urls import re_path
from . import consumers # consumers 임포트

websocket_urlpatterns = [
    # 'ws/chat/' URL 경로를 ChatConsumer와 매핑
    re_path(r'ws/chat/$', consumers.ChatConsumer.as_asgi()),
]