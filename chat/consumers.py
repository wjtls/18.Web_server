# chat/consumers.py
import json  # JSON 데이터 처리
from channels.generic.websocket import AsyncWebsocketConsumer  # 비동기 WebSocket 컨슈머
from django.contrib.auth import get_user_model  # Django 사용자 모델 가져오기
from django.utils import timezone  # 시간 관련 유틸리티
from datetime import timedelta  # 시간 간격 계산
from channels.db import database_sync_to_async  # 비동기 환경에서 동기 DB 작업 실행

# main 앱의 models.py 에 TIER_THRESHOLDS 상수가 정의되어 있다고 가정
# ★★★ 네 main.models 경로와 TIER_THRESHOLDS 이름 확인 필요 ★★★
from main.models import TIER_THRESHOLDS
from .models import ChatMessage  # chat 앱의 ChatMessage 모델

User = get_user_model()  # 현재 Django 프로젝트에서 사용하는 사용자 모델 가져오기


class ChatConsumer(AsyncWebsocketConsumer):
    # WebSocket 연결이 처음 시도될 때 실행
    async def connect(self):
        self.room_name = 'lobby'  # 모든 사용자가 참여할 채팅방 이름 (단일 방)
        self.room_group_name = f'chat_{self.room_name}'  # Channels 그룹 이름 (채팅방 식별자)

        # 현재 요청을 보낸 사용자(self.scope['user'])가 로그인(인증)된 사용자인지 확인
        if not self.scope['user'].is_authenticated:
            await self.close()  # 인증되지 않은 사용자는 WebSocket 연결 거부
            return

        # 현재 WebSocket 채널을 특정 그룹(채팅방)에 추가
        # 같은 그룹에 있는 모든 채널은 서로 메시지를 주고받을 수 있게 됨
        await self.channel_layer.group_add(
            self.room_group_name,  # 참여할 그룹 이름
            self.channel_name  # 현재 채널의 고유 이름
        )

        # 클라이언트에게 WebSocket 연결 성공 알림
        await self.accept()

        print(
            f"[{timezone.now().strftime('%Y-%m-%d %H:%M:%S')}] User {self.scope['user'].username} connected to chat room: {self.room_group_name}")

        # === 이전 대화 내용 불러와서 현재 사용자에게만 전송 ===
        # 최근 10일 이내의 메시지 중, 최신 50개만 가져오기
        await self.send_previous_messages(limit=50)

    # WebSocket 연결이 끊어졌을 때 실행
    async def disconnect(self, close_code):
        # 사용자가 인증된 경우에만 그룹에서 제거 시도 (연결 시 추가했으므로)
        if self.scope['user'].is_authenticated:
            # 현재 WebSocket 채널을 그룹(채팅방)에서 제거
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
            print(
                f"[{timezone.now().strftime('%Y-%m-%d %H:%M:%S')}] User {self.scope['user'].username} disconnected from chat room: {self.room_group_name}")

    # 클라이언트(브라우저)로부터 WebSocket을 통해 메시지를 받았을 때 실행
    async def receive(self, text_data):
        # 받은 메시지(text_data)는 JSON 문자열 형식이므로 파싱
        text_data_json = json.loads(text_data)
        # JSON 객체에서 'message' 키의 값을 가져오고, 양쪽 공백 제거
        message_text = text_data_json.get('message', '').strip()

        if not message_text:  # 메시지 내용이 비어있으면 무시
            return

        user = self.scope['user']  # 메시지를 보낸 사용자 객체

        # 사용자 상세 정보 (닉네임, 레벨, 티어 이모티콘) 비동기로 가져오기
        user_details = await self.get_user_chat_details_async(user)

        # 메시지 저장 및 전송에 사용할 현재 시간 기록
        current_timestamp = timezone.now()

        # === 받은 메시지를 데이터베이스에 저장 ===
        await self.save_message_to_db_async(user, message_text, self.room_name, current_timestamp)

        # === 같은 채팅방(그룹)에 있는 모든 사용자에게 메시지 브로드캐스팅 ===
        # group_send를 사용하면 그룹 내 모든 Consumer에게 'type'에 지정된 이름의 메서드 호출을 요청
        await self.channel_layer.group_send(
            self.room_group_name,  # 메시지를 보낼 그룹 이름
            {
                'type': 'chat_message_broadcast',  # 이 메시지를 처리할 핸들러 메서드 이름
                'message_text': message_text,
                'username': user.username,  # 실제 사용자 이름 (고유 식별용)
                'nickname': user_details['nickname'],  # 화면에 표시될 닉네임
                'tier_emoji': user_details['tier_emoji'],  # 티어 이모티콘
                'level': user_details['level'],  # 사용자 레벨
                'timestamp': current_timestamp.isoformat()  # ISO 형식의 타임스탬프 문자열
            }
        )

    # 위 group_send에서 'type': 'chat_message_broadcast'로 지정된 메시지를 받았을 때 실행되는 메서드
    # (이 Consumer 인스턴스 자신이 보낸 메시지 포함, 그룹 내 모든 Consumer가 이 메서드 실행)
    async def chat_message_broadcast(self, event):
        # 이벤트 객체(event)에서 메시지 내용 추출
        # 클라이언트에게 최종적으로 전송할 데이터 구성
        await self.send(text_data=json.dumps({
            'message_text': event['message_text'],
            'username': event['username'],
            'nickname': event['nickname'],
            'tier_emoji': event['tier_emoji'],
            'level': event['level'],
            'timestamp': event.get('timestamp')  # 타임스탬프 포함 (없을 수도 있으므로 get 사용)
        }))

    # === 데이터베이스 작업을 위한 비동기 헬퍼 메서드들 ===
    # database_sync_to_async: Django의 동기적인 ORM 작업을 비동기 컨텍스트에서 안전하게 실행하도록 변환

    @database_sync_to_async
    def get_user_chat_details_async(self, user_obj):
        # User 모델에서 채팅 표시에 필요한 정보 가져오기
        # ★★★ User 모델에 nickname, current_level, user_tier_xp, profit_rank 필드/프로퍼티 및
        # get_tier_info() 메서드가 정의되어 있다고 가정함. 네 main/models.py 확인 필요! ★★★
        nickname = user_obj.nickname if user_obj.nickname else user_obj.username
        level = user_obj.current_level

        tier_emoji = '🌱'  # 기본 이모티콘 (티어 정보 없을 시)
        user_tier_xp = getattr(user_obj, 'user_tier_xp', 0)  # user_tier_xp 필드가 없을 수 있으므로 getattr 사용

        is_champion_ranker = False
        if hasattr(user_obj, 'profit_rank') and user_obj.profit_rank is not None and 1 <= user_obj.profit_rank <= 50:
            champion_xp_threshold = next((t[0] for t in TIER_THRESHOLDS if t[1] == 'Champion'), float('inf'))
            if user_tier_xp >= champion_xp_threshold:
                tier_info = user_obj.get_tier_info()  # 이 메서드는 동기적으로 User 객체 내 정보 반환 가정
                tier_emoji = tier_info.get('image', tier_emoji)
                is_champion_ranker = True

        if not is_champion_ranker:  # 일반 티어 계산
            for threshold, name, emoji_or_image in TIER_THRESHOLDS:
                if user_tier_xp >= threshold:
                    # TIER_THRESHOLDS의 세 번째 값이 이모지 문자열이라고 가정
                    tier_emoji = emoji_or_image
                    break
        return {'nickname': nickname, 'level': level, 'tier_emoji': tier_emoji}

    @database_sync_to_async
    def save_message_to_db_async(self, user, message_text, room_name, timestamp_obj):
        # ChatMessage 객체를 생성하고 데이터베이스에 저장
        ChatMessage.objects.create(sender=user, message=message_text, room_name=room_name, timestamp=timestamp_obj)
        print(
            f"[{timezone.now().strftime('%Y-%m-%d %H:%M:%S')}] Message saved to DB: {user.username} in {room_name}: {message_text[:20]}...")

    @database_sync_to_async
    def get_previous_messages_from_db_async(self, room_name, limit_count):
        # 최근 10일 이내의 메시지만 필터링 대상
        ten_days_ago = timezone.now() - timedelta(days=10)

        # DB에서 메시지 조회:
        # 1. 지정된 방 이름(room_name)
        # 2. 10일 이내 (timestamp__gte=ten_days_ago)
        # 3. 발신자(sender) 정보도 함께 로드 (select_related로 N+1 쿼리 문제 방지)
        # 4. 최신 메시지 순서로 정렬 (order_by('-timestamp'))
        # 5. 최대 limit_count 개수만큼만 가져오기 ([:limit_count])
        messages_queryset = ChatMessage.objects.filter(
            room_name=room_name,
            timestamp__gte=ten_days_ago
        ).select_related('sender').order_by('-timestamp')[:limit_count]

        chat_history_for_client = []
        # 가져온 메시지 목록(최신순)을 오래된 순서로 뒤집어서 클라이언트에 전달 (화면 표시는 보통 위에서 아래로)
        for msg_db_obj in reversed(messages_queryset):
            sender_user_obj = msg_db_obj.sender  # 이미 로드된 sender 객체

            # 각 메시지 발신자의 상세 정보 가져오기
            # get_user_chat_details_async는 비동기 함수이므로 여기서 바로 호출하지 않고,
            # 필요한 정보만 동기적으로 구성 (User 모델의 필드/프로퍼티 직접 접근)
            # ★★★ 이 부분도 User 모델 구조에 따라 수정 필요 ★★★
            nickname = sender_user_obj.nickname if sender_user_obj.nickname else sender_user_obj.username
            level = sender_user_obj.current_level
            # 티어 정보는 User 객체의 get_tier_info() 메서드 (동기) 호출 가정
            tier_info_dict = sender_user_obj.get_tier_info()
            tier_emoji_str = tier_info_dict.get('image', '🌱')

            chat_history_for_client.append({
                'message_text': msg_db_obj.message,
                'username': sender_user_obj.username,
                'nickname': nickname,
                'tier_emoji': tier_emoji_str,
                'level': level,
                'timestamp': msg_db_obj.timestamp.isoformat()  # ISO 형식의 시간 문자열
            })
        return chat_history_for_client

    # 현재 접속한 클라이언트에게 이전 메시지들을 전송하는 메서드
    async def send_previous_messages(self, limit=50):
        previous_messages_list = await self.get_previous_messages_from_db_async(self.room_name, limit)
        for single_message_data in previous_messages_list:
            # 각 이전 메시지를 현재 클라이언트에게만 전송 (chat_message_broadcast와 동일한 포맷 사용)
            await self.send(text_data=json.dumps(single_message_data))