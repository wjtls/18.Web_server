# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils import timezone # 타임스탬프용

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # 사용자가 인증되었는지 확인
        if self.scope["user"].is_authenticated:
            self.user = self.scope["user"] # 사용자 객체 가져오기
            self.room_group_name = 'general_chat' # 모든 사용자를 위한 간단한 그룹 이름

            # 채팅방 그룹에 참가
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            await self.accept() # 웹소켓 연결 수락
        else:
            # 로그인하지 않은 사용자는 연결 거부
            await self.close()

    async def disconnect(self, close_code):
        # 연결되어 있었다면 채팅방 그룹에서 나가기
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    # 웹소켓 클라이언트(JavaScript)로부터 메시지 수신
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_text = text_data_json['message'].strip() # 메시지 텍스트 가져오기 (공백 제거)

        if message_text: # 빈 메시지는 처리하지 않음
            # 브로드캐스트할 메시지 데이터 준비
            message_data = {
                'type': 'chat_message', # 아래 'chat_message' 메소드와 연결됨
                'message': message_text,
                'username': self.user.username,
                'level': self.user.level,       # User 모델에 'level' 필드가 있다고 가정
                'tier': self.user.user_tier,  # User 모델에 'user_tier' 필드가 있다고 가정
                'timestamp': timezone.now().strftime('%I:%M %p').lstrip('0').replace(' AM', 'AM').replace(' PM', 'PM') # 시간 형식 지정
            }

            # 채팅방 그룹에 메시지 전송
            await self.channel_layer.group_send(
                self.room_group_name,
                message_data # 준비된 데이터 전송
            )

    # 채팅방 그룹으로부터 메시지를 받아 웹소켓 클라이언트로 전송
    async def chat_message(self, event):
        # 웹소켓(JavaScript)으로 메시지 데이터 전송
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'username': event['username'],
            'level': event['level'],
            'tier': event['tier'],
            'timestamp': event['timestamp'],
        }))