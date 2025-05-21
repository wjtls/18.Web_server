
import os
import sys # sys 모듈을 import 합니다.
import django
from decimal import Decimal

# --- ▼▼▼ 프로젝트 루트 경로를 sys.path에 추가하는 코드 ▼▼▼ ---
# 이 스크립트 파일(put_title.py)이 .../c_web_env/main/ 폴더 안에 있다고 가정합니다.
# 프로젝트 루트 폴더(manage.py 파일이 있고, 'chart' 패키지가 있는 곳)는 .../c_web_env/ 입니다.
SCRIPT_ABSPATH = os.path.abspath(__file__) # 현재 스크립트의 절대 경로
SCRIPT_DIR = os.path.dirname(SCRIPT_ABSPATH) # 현재 스크립트가 있는 디렉토리 (예: .../c_web_env/main)
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR) # 그 부모 디렉토리 (예: .../c_web_env)

# sys.path에 프로젝트 루트가 이미 포함되어 있지 않다면 추가합니다.
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
    print(f"DEBUG [put_title.py]: sys.path에 프로젝트 루트 추가됨: {PROJECT_ROOT}")
else:
    print(f"DEBUG [put_title.py]: 프로젝트 루트가 이미 sys.path에 있음: {PROJECT_ROOT}")
# --- ▲▲▲ sys.path 추가 코드 끝 ▲▲▲ ---


# Django 설정 로드
# 'chart.settings'는 사용자님의 실제 Django 프로젝트 settings.py 파일의 파이썬 경로입니다.
# (예: 프로젝트 루트에 'chart'라는 폴더(패키지)가 있고 그 안에 settings.py가 있는 구조)
DJANGO_SETTINGS_MODULE_NAME = 'chart.settings' # ★★★ 이 부분이 실제 프로젝트 설정과 일치하는지 확인! ★★★
os.environ.setdefault('DJANGO_SETTINGS_MODULE', DJANGO_SETTINGS_MODULE_NAME)

try:
    print(f"DEBUG [put_title.py]: Django 설정 로드 시도: '{DJANGO_SETTINGS_MODULE_NAME}'")
    django.setup()
    print(f"DEBUG [put_title.py]: Django setup 완료!")
except Exception as e:
    print(f"DEBUG [put_title.py]: !!! Django setup 중 심각한 오류 발생: {e} !!!")
    print(f"DEBUG [put_title.py]: 현재 sys.path: {sys.path}")
    # settings.py 파일이 실제로 존재하는지 예상 경로를 확인해봅니다.
    # 'chart' 부분을 실제 settings.py가 있는 폴더명으로 바꿔야 할 수 있습니다.
    expected_settings_path = os.path.join(PROJECT_ROOT, DJANGO_SETTINGS_MODULE_NAME.split('.')[0], 'settings.py')
    print(f"DEBUG [put_title.py]: 예상되는 settings.py 파일 경로: {expected_settings_path}")
    print(f"DEBUG [put_title.py]: 해당 경로에 settings.py 파일 존재 여부: {os.path.exists(expected_settings_path)}")
    print("스크립트를 중단합니다. DJANGO_SETTINGS_MODULE 경로 또는 프로젝트 구조를 확인해주세요.")
    raise # 오류를 다시 발생시켜서 전체 트레이스백 확인


# Django 설정을 성공적으로 로드한 후에 모델을 import 합니다.
# Title 모델이 main/models.py에 있다고 가정합니다.
try:
    from main.models import Title # ★★★ Title 모델의 실제 위치에 맞게 수정! ★★★
    print("DEBUG [put_title.py]: main.models 에서 Title 모델 import 성공.")
except ImportError as e:
    print(f"DEBUG [put_title.py]: !!! main.models 에서 Title 모델 import 실패: {e} !!!")
    print("main 앱이 INSTALLED_APPS에 있고, main/models.py에 Title 모델이 정의되어 있는지 확인해주세요.")
    raise
except Exception as e: # 기타 모델 로딩 관련 오류
    print(f"DEBUG [put_title.py]: !!! 모델 로딩 중 알 수 없는 오류: {e} !!!")
    raise
def add_titles():
    print("칭호 데이터 추가 시작...")
    titles_to_create = [
        {
            'title_id':'beginner',
            'defaults':{
                'name': '초보',
                'description': '이제 막 여정을 시작한 투자 꿈나무입니다.',
                'price_asi': Decimal('10.00'),
                'purchase_conditions': {'level_required': 1},
                'is_purchasable': True,
                'is_color_selectable': True,
                'default_display_color': '#A0A0A0',
                'order': 10
            }
        },
        {
            'title_id':'intermediate',
            'defaults':{
                'name': '중수',
                'description': '어느덧 투자에 익숙해진 중급 모험가입니다.',
                'price_asi': Decimal('50.00'),
                'price_sim_cash': Decimal('500000.00'),
                'purchase_conditions': {'level_required': 5},
                'is_purchasable': True,
                'is_color_selectable': True,
                'default_display_color': '#6DD400',
                'order': 20
            }
        },
        {
            'title_id':'advanced',
            'defaults':{
                'name': '고수',
                'description': '투자의 흐름을 읽을 줄 아는 숙련된 전략가입니다.',
                'price_asi': Decimal('200.00'),
                'price_cash': Decimal('10000'),
                'purchase_conditions': {'level_required': 10, 'min_total_trades': 50},
                'is_purchasable': True,
                'is_color_selectable': True,
                'default_display_color': '#0091FF',
                'order': 30
            }
        },
        {
            'title_id':'expert',
            'defaults':{
                'name': '초고수',
                'description': '시장을 꿰뚫어보는 경지에 이른 전설적인 투자자입니다.',
                'price_asi': Decimal('500.00'),
                'purchase_conditions': {'level_required': 20, 'min_profit_percentage': 50.0},
                'is_purchasable': True,
                'is_color_selectable': True,
                'default_display_color': '#C900FF',
                'order': 40
            }
        },
        {
            'title_id':'millionaire_sim',
            'defaults':{
                'name': '백만장자',
                'description': '투자 세계에서 백만 달러의 자산을 달성했습니다!',
                'price_asi': None, 'price_cash': None, 'price_sim_cash': None,
                'purchase_conditions': {'min_sim_portfolio_value': 1000000},
                'is_purchasable': False,
                'is_color_selectable': True,
                'default_display_color': '#FFD700',
                'order': 50
            }
        },
        {
            'title_id':'billionaire_sim',
            'defaults':{
                'name': '억만장자',
                'description': '투자 세계에서 억만 달러의 자산을 달성한 거물입니다!',
                'price_asi': None, 'price_cash': None, 'price_sim_cash': None,
                'purchase_conditions': {'min_sim_portfolio_value': 1000000000},
                'is_purchasable': False,
                'is_color_selectable': True,
                'default_display_color': '#E5E4E2',
                'order': 60
            }
        },
    ]

    for title_data in titles_to_create:
        obj, created = Title.objects.update_or_create(
            title_id=title_data['title_id'],
            defaults=title_data['defaults']
        )
        if created:
            print(f"칭호 생성됨: {obj.name}")
        else:
            print(f"칭호 업데이트됨: {obj.name}")

    print("칭호 데이터 추가/업데이트 작업 완료.")


if __name__ == '__main__':
    print(f"DEBUG [put_title.py]: __name__ is '{__name__}', 스크립트 실행 시작.")
    add_titles()
    print(f"DEBUG [put_title.py]: 스크립트 실행 완료.")