# 알람보내는 task

import os
import json
import firebase_admin
from aiohttp import request
from celery import shared_task
from django.core.cache import cache
from firebase_admin import messaging
from .models import AlarmSubscription, Notification, UserDevice
from firebase_admin import credentials
from django.conf import settings
# --- 설정값 (views_AI.py와 별개로 tasks.py가 자체적으로 가짐) ---
BASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "b_strategy_AI")




def _ensure_firebase_initialized():
    """
    Firebase Admin SDK가 초기화되지 않았다면 초기화합니다.
    초기화된 앱 객체를 반환합니다.
    """
    if not firebase_admin._apps:
        try:
            cred = credentials.Certificate(settings.GOOGLE_SERVICE_ACCOUNT_KEY_PATH)
            # [수정] 초기화된 앱을 변수에 저장
            app = firebase_admin.initialize_app(cred)
            print("[tasks.py] Firebase Admin SDK를 이 태스크에서 초기화했습니다.")
            return app
        except Exception as e:
            print(f"[tasks.py] 태스크 내 Firebase 초기화 실패: {e}")
            raise e
    # 이미 초기화되었다면, 기본 앱을 가져와서 반환
    return firebase_admin.get_app()













#알람타겟
TRADER_CONFIGS = {
    'trader1': {
        'file_path': '2_AI_APPO_LS_stock/traj/backtest_result.json',
    },
    'trader2': {
        'file_path': '2_AI_APPO_LS_stock_TQQQ_61_ver2/traj/backtest_result.json',
    },
    'trader3': {
        'file_path': '2_AI_APPO_LS_stock_TQQQ_61_ver3/traj/backtest_result.json',
    },
    'trader4': {
        'file_path': '2_AI_APPO_LS_stock_AAPU_31/traj/backtest_result.json',
    },
    'trader5': {
        'file_path': '2_AI_APPO_LS_stock_TSLL_61/traj/backtest_result.json',
    }
}


def get_position_text(action):
    """action 코드에 따라 사용자에게 보여줄 텍스트를 반환합니다."""
    if str(action) == '2': return '분할 매수 시작'
    if str(action) == '0': return '분할 매도 시작'
    # '1'(관망)은 포지션 변경이 아니므로 알람을 보내지 않음
    return None


def get_latest_action_from_file(trader_id: str):

    """
    [Task 전용 로직] 지정된 트레이더의 데이터 파일에서 마지막 action 값을 직접 읽어옵니다.
    """
    config = TRADER_CONFIGS.get(trader_id)
    if not config:
        print(f"[{trader_id}] 설정 없음")
        return None

    try:
        full_path = os.path.join(BASE_PATH, config['file_path'])
        data_lines = []
        with open(full_path, 'r', encoding='utf-8') as file:
            for line in file:
                data_lines.append(json.loads(line.strip()))

        # 마지막 action 값만 빠르게 찾기
        for item in reversed(data_lines):
            if item.get('index') == 'action_data':
                action_list = item.get('0', {}).get('long', [])
                if action_list:
                    last_action = action_list[-1]
                    # action이 [2], [0] 같은 리스트 형태일 수 있으므로 첫 번째 요소 추출
                    return str(last_action[0] if isinstance(last_action, list) else last_action)
        return None
    except FileNotFoundError:
        print(f"[{trader_id}] 파일 읽기 실패: 파일을 찾을 수 없습니다. 경로: {full_path}")
        return None
    except Exception as e:
        print(f"[{trader_id}] 파일에서 action 데이터 읽기 실패: {e}")
        return None


@shared_task
def check_ai_trader_signals():
    print("===== AI 트레이더 시그널 체크 시작 =====")
    firebase_app = _ensure_firebase_initialized()
    trader_ids = TRADER_CONFIGS.keys()

    for trader_id in trader_ids:
        # 1. 최신 action 값을 파일에서 직접 가져오기
        current_action = get_latest_action_from_file(trader_id)
        if current_action is None:
            continue

        # 2. 마지막으로 저장된 포지션(action) 가져오기 (Redis 캐시 사용)
        last_action_key = f'last_action_{trader_id}'
        last_action = cache.get(last_action_key)

        # 3. 포지션 변경 감지 (action 코드가 다를 때)
        if current_action != last_action:
            current_position_text = get_position_text(current_action)

            # 4. 의미 있는 포지션 변경일 때만 알람 발송 (매수/매도 시작)
            if current_position_text:
                print(f"포지션 변경 감지: {trader_id} - '{last_action}' -> '{current_action}' ({current_position_text})")

                subscriptions = AlarmSubscription.objects.filter(trader_id=trader_id, is_active=True).select_related(
                    'user')
                user_ids_to_notify = [sub.user_id for sub in subscriptions]

                if user_ids_to_notify:
                    notifications_to_create = [
                        Notification(
                            user_id=user_id,
                            title=f"{trader_id} 포지션 변경 알림",
                            message=f"{trader_id}의 포지션이 '{current_position_text}'으로 변경되었습니다."
                        ) for user_id in user_ids_to_notify
                    ]
                    Notification.objects.bulk_create(notifications_to_create)

                    devices = UserDevice.objects.filter(user_id__in=user_ids_to_notify)
                    fcm_tokens = [device.fcm_token for device in devices if device.fcm_token]
                    print('fcm_tokens :',fcm_tokens)
                    if fcm_tokens:
                        message = messaging.MulticastMessage(
                            notification=messaging.Notification(
                                title=f"{trader_id} 포지션 변경",
                                body=f"{trader_id}가 '{current_position_text}' 했습니다."
                            ),
                            tokens=list(set(fcm_tokens))
                        )
                        response = messaging.send_multicast(message,app=firebase_app)   #알람전송
                        print(f'{response.success_count}개의 알람 전송 성공')

            # 8. 마지막 포지션을 현재 포지션으로 캐시에 업데이트
            cache.set(last_action_key, current_action, timeout=None)

    print("===== AI 트레이더 시그널 체크 종료 =====")


@shared_task
def send_periodic_quiz_notification():
    """
    모든 사용자에게 주기적으로 퀴즈 참여 푸시 알림을 보냅니다. (상세 디버깅 모드)
    """
    firebase_app = None
    try:
        firebase_app = _ensure_firebase_initialized()
    except Exception as e:
        print(f"퀴즈 알람 태스크 시작 중 Firebase 초기화 실패: {e}")
        return  # 초기화 실패 시 작업 중단

    print("===== 주기적 퀴즈 알람 발송 시작 =====")

    devices = UserDevice.objects.filter(user__quiz_alarm_enabled=True)
    fcm_tokens = [device.fcm_token for device in devices if device.fcm_token]

    if not fcm_tokens:
        print("퀴즈 알람을 보낼 기기가 없습니다.")
        return

    print(f"{len(fcm_tokens)}개의 기기로 퀴즈 알람을 보냅니다.")

    message = messaging.MulticastMessage(
        notification=messaging.Notification(
            title="새로운 퀴즈 도착! 📬",
            body="오늘의 주가 예측 퀴즈에 참여해보세요!"
        ),
        data={'screen': 'PlatformQuiz'},
        tokens=list(set(fcm_tokens))
    )

    try:
        # ▼▼▼▼▼ 최종 디버깅 로그 추가 ▼▼▼▼▼
        print("\n--- PUSH NOTIFICATION DEBUG START ---")
        if firebase_app:
            print(f"1. Firebase App Name: {firebase_app.name}")
            print(f"2. Firebase App Project ID: {firebase_app.project_id}")
        else:
            print("1. Firebase App: 초기화되지 않음")

        print(f"3. FCM Tokens to Send: {fcm_tokens}")
        print(f"4. Message Title: {message.notification.title}")
        print(f"5. Message Body: {message.notification.body}")
        print("------------------------------------\n")
        # ▲▲▲▲▲ 디버깅 로그 끝 ▲▲▲▲▲

        response = messaging.send_multicast(message, app=firebase_app)
        print(f'{response.success_count}개의 퀴즈 알람 전송 성공')

    except Exception as e:
        print(f"퀴즈 알람 발송 중 오류 발생: {e}")

    print("===== 주기적 퀴즈 알람 발송 종료 =====")

