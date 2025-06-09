import firebase_admin
from firebase_admin import credentials
from django.conf import settings
import os


def initialize_firebase_app():
    """
    Firebase Admin SDK를 초기화합니다.
    settings.py에 정의된 서비스 계정 키 파일 경로를 사용합니다.
    """
    try:
        # 이미 초기화되었는지 확인하여 중복 초기화 방지
        if not firebase_admin._apps:
            # GOOGLE_SERVICE_ACCOUNT_KEY_PATH는 settings.py에 정의되어 있어야 합니다.
            service_account_key_path = settings.GOOGLE_SERVICE_ACCOUNT_KEY_PATH

            if not os.path.exists(service_account_key_path):
                print(f"Firebase 서비스 계정 키 파일이 없습니다: {service_account_key_path}")
                return

            cred = credentials.Certificate(service_account_key_path)
            firebase_admin.initialize_app(cred)
            print("Firebase Admin SDK가 성공적으로 초기화되었습니다.")
    except Exception as e:
        print(f"Firebase Admin SDK 초기화 중 오류 발생: {e}")


# Django 앱이 로드될 때 이 함수를 호출하여 초기화 실행
initialize_firebase_app()