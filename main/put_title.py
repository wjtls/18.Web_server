#main/put_title.py

import os
import sys # sys 모듈을 import 합니다.
import django
from decimal import Decimal

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


try:
    from main.models import Title #
    print("DEBUG [put_title.py]: main.models 에서 Title 모델 import 성공.")
except ImportError as e:
    print(f"DEBUG [put_title.py]: !!! main.models 에서 Title 모델 import 실패: {e} !!!")
    print("main 앱이 INSTALLED_APPS에 있고, main/models.py에 Title 모델이 정의되어 있는지 확인해주세요.")
    raise
except Exception as e: # 기타 모델 로딩 관련 오류
    print(f"DEBUG [put_title.py]: !!! 모델 로딩 중 알 수 없는 오류: {e} !!!")
    raise

def add_titles():
    print("칭호 데이터 추가/업데이트 시작...")
    titles_to_create = [
        # --- 일반 칭호 ---
        {
            'title_id':'title_beginner',
            'defaults':{
                'name': '초보', 'description': '투자의 세계에 첫 발을 내딛은 새싹 투자자!',
                'price_sim_cash': Decimal('0'), 'is_purchasable': True, 'is_achievement_title': False,
                'purchase_conditions': {}, # 특별 조건 없음
                'is_color_selectable': True, 'default_display_color': '#CD7F32', 'order': 10
            }
        },
        {
            'title_id':'title_intermediate',
            'defaults':{
                'name': '중수', 'description': '이제 제법 시장의 흐름이 보이기 시작합니다.',
                'price_sim_cash': Decimal('0'), 'is_purchasable': True, 'is_achievement_title': False,
                'purchase_conditions': {'level_gte': 5},
                'is_color_selectable': True, 'default_display_color': '#C0C0C0', 'order': 20
            }
        },
        {
            'title_id':'title_expert',
            'defaults':{
                'name': '고수', 'description': '예리한 분석과 과감한 판단, 당신은 이미 고수!',
                'price_sim_cash': Decimal('0'), 'is_purchasable': True, 'is_achievement_title': False,
                'purchase_conditions': {'level_gte': 10},
                'is_color_selectable': True, 'default_display_color': '#FFD700', 'order': 30
            }
        },
        {
            'title_id':'title_master',
            'defaults':{
                'name': '초고수', 'description': '시장을 예측하는 자, 투자의 정점에 서다.',
                'price_sim_cash': Decimal('0'), 'is_purchasable': True, 'is_achievement_title': False,
                'purchase_conditions': {'level_gte': 20},
                'is_color_selectable': True, 'default_display_color': '#E5E4E2', 'order': 40
            }
        },
        {
            'title_id':'title_alpha_tester', # 신규: 알파테스터
            'defaults':{
                'name': '알파테스터', 'description': '최초의 길을 개척한 선구자, 감사합니다!',
                'price_sim_cash': Decimal('0'), 'is_purchasable': True, # 또는 특정 유저에게만 지급 시 False
                'is_achievement_title': False, # 일반 칭호로 분류
                'purchase_conditions': {}, # 예: 특정 ID만 구매 가능하게 하려면 별도 로직 필요
                'is_color_selectable': True, 'default_display_color': '#7CFC00', 'order': 5
            }
        },
        # --- 업적 칭호 ---
        {
            'title_id':'title_millionaire',
            'defaults':{
                'name': '백만장자', 'description': '모의투자 백만 달러 달성! 부의 첫걸음.',
                'price_sim_cash': Decimal('0'), 'is_purchasable': True, 'is_achievement_title': True,
                'purchase_conditions': {'sim_cash_gte': 1000000},
                'is_color_selectable': True, 'default_display_color': '#B9F2FF', 'order': 100
            }
        },
        {
            'title_id':'title_billionaire',
            'defaults':{
                'name': '억만장자', 'description': '모의투자 억만 달러의 위엄, 살아있는 전설!',
                'price_sim_cash': Decimal('0'), 'is_purchasable': True, 'is_achievement_title': True,
                'purchase_conditions': {'sim_cash_gte': 1000000000},
                'is_color_selectable': True, 'default_display_color': '#7DF9FF', 'order': 110
            }
        },
        {
            'title_id':'title_vip', # 신규: VIP
            'defaults':{
                'name': 'VIP', 'description': '천만 달러의 품격, 당신은 우리 플랫폼의 귀빈입니다.',
                'price_sim_cash': Decimal('0'), 'is_purchasable': True, 'is_achievement_title': True,
                'purchase_conditions': {'sim_cash_gte': 10000000}, # 모의투자금액 천만 이상
                'is_color_selectable': True, 'default_display_color': '#FF69B4', 'order': 120
            }
        },
        {
            'title_id':'title_vvip', # 신규: VVIP
            'defaults':{
                'name': 'VVIP', 'description': '억만 달러를 넘어선 투자 거물, VVIP의 명예를 드립니다.',
                'price_sim_cash': Decimal('0'), 'is_purchasable': True, 'is_achievement_title': True,
                'purchase_conditions': {'sim_cash_gte': 100000000}, # 모의투자금액 1억 이상
                'is_color_selectable': True, 'default_display_color': '#BA55D3', 'order': 130
            }
        },
        {
            'title_id':'title_lucky_one', # 신규: 운이좋은
            'defaults':{
                'name': '운이 좋은', 'description': '행운도 실력! 백만 달러의 주인공이 되셨군요!',
                'price_sim_cash': Decimal('0'), 'is_purchasable': True, 'is_achievement_title': True,
                'purchase_conditions': {'sim_cash_gte': 1000000}, # 모의투자금액 백만 이상
                'is_color_selectable': True, 'default_display_color': '#FFD700', 'order': 140
            }
        },
        {
            'title_id':'title_all_in_broke', # 신규: 전재산을탕진한
            'defaults':{
                'name': '전재산을 탕진한', 'description': '괜찮아요, 다시 시작하면 되죠! 꺾이지 않는 마음.',
                'price_sim_cash': Decimal('0'), 'is_purchasable': True, 'is_achievement_title': True,
                'purchase_conditions': {'sim_cash_lte': 100}, # 모의투자금액 100 이하
                'is_color_selectable': True, 'default_display_color': '#808080', 'order': 150
            }
        },
        {
            'title_id':'title_prophet', # 신규: 예언가
            'defaults':{
                'name': '예언가', 'description': '천 번의 예측, 만 번의 성공! 미래를 보는 자.',
                'price_sim_cash': Decimal('0'), 'is_purchasable': True, 'is_achievement_title': True,
                'purchase_conditions': {'level_gte': 10, 'quiz_wins_gte': 1000}, # 레벨 10 이상, 승리 1000 이상
                'is_color_selectable': True, 'default_display_color': '#483D8B', 'order': 160
            }
        },
        {
            'title_id': 'title_GM',  # 신규: 예언가
            'defaults': {
                'name': 'GM', 'description': '운영자만 소지 가능한 칭호',
                'price_sim_cash': Decimal('0'), 'is_purchasable': True, 'is_achievement_title': True,
                'purchase_conditions': {'level_gte': 1000000, 'quiz_wins_gte': 10000000},  # 레벨 10 이상, 승리 1000 이상
                'is_color_selectable': True, 'default_display_color': '#BA55D3', 'order': 1
            }
        },
    ]

    for title_data in titles_to_create:
        # Title 모델에 정의된 필드만 defaults에 포함되도록 필터링
        valid_defaults = {}
        for key, value in title_data['defaults'].items():
            if hasattr(Title, key): # Title 모델에 해당 속성(필드)이 있는지 확인
                valid_defaults[key] = value
            else:
                print(f"경고: Title 모델에 '{key}' 필드가 없습니다. '{title_data['title_id']}' 칭호의 해당 속성은 무시됩니다.")

        obj, created = Title.objects.update_or_create(
            title_id=title_data['title_id'],
            defaults=valid_defaults
        )
        if created:
            print(f"칭호 생성됨: {obj.name} (ID: {obj.title_id})")
        else:
            print(f"칭호 업데이트됨: {obj.name} (ID: {obj.title_id})")

    print("칭호 데이터 추가/업데이트 작업 완료.")





if __name__ == '__main__':
    print(f"DEBUG [put_title.py]: __name__ is '{__name__}', 스크립트 실행 시작.")
    add_titles()
    print(f"DEBUG [put_title.py]: 스크립트 실행 완료.")