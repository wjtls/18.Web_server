from django.shortcuts import render
from django.http import HttpResponse
import requests
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate # 자동 로그인을 위해 login 추가
from django.contrib import messages # 사용자에게 피드백 메시지를 보여주기 위함
from django.db.models import F # DB 업데이트 시 원자적 연산 지원
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import StrategyPageSubscription # 모델 import

def index(request):
    return render(request,"main/index_homepage.html")

def index2_simulator(request):
    return render(request,"main/index2_simulator.html")

def index3_strategy(request):
    return render(request,"main/index3_strategy.html")

@login_required # 로그인 필수
def index3_strategy_(request): # 뷰 함수 이름은 실제 사용하는 것으로
    user = request.user
    # 현재 사용자가 활성화된(만료되지 않은) 전략 페이지 구독권을 가지고 있는지 확인
    is_subscribed = StrategyPageSubscription.objects.filter(
        subscriber=user,
        expires_at__gt=timezone.now() # 현재 시간보다 만료 시간이 미래인 구독 조회
    ).exists() # 하나라도 존재하면 True

    if not is_subscribed:
        # 구독권이 없으면 마켓 페이지로 리다이렉트 (또는 에러 메시지 표시)
        # from django.contrib import messages
        # messages.warning(request, "전략 페이지 접근 권한이 없습니다. 마켓에서 구독권을 구매해주세요.")
        return redirect('index4_user_market') # 마켓 페이지의 URL 이름 사용

    # 구독 중인 사용자에게만 전략 페이지 보여주기
    context = {
        # ... 전략 페이지에 필요한 데이터 ...
    }
    return render(request, 'main/index3_strategy.html', context) # 실제 템플릿 경로 확인



def index4_user_market(request):
    return render(request,"main/index4_user_market.html")

def chat_return(request): #채팅을 리턴
    data = request.POST.get("message")
    print(data,'채팅창에 입력된 문자')
    return HttpResponse(data)


from django.shortcuts import render, redirect
from django.contrib import messages
# from django.contrib.auth.hashers import make_password # create_user 사용 시 필요 없음
from .models import User # 사용자 모델 import

def register_view(request):
    """
    회원가입 요청을 처리하는 뷰 함수 (POST 요청만 처리)
    """
    if request.method == 'POST':
        # 폼에서 데이터 가져오기
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        terms_accepted = request.POST.get('terms_accepted')

        # 1. 필수 항목 검사
        if not all([username, password, confirm_password]):
            messages.error(request, '모든 필수 항목을 입력해주세요.')
            return redirect('_register_modal.html')

        # 2. 비밀번호 일치 확인
        if password != confirm_password:
            messages.warning(request, '비밀번호가 일치하지 않습니다.')
            return redirect('_register_modal.html')

        # 3. 약관 동의 확인
        if terms_accepted != 'true':
            messages.warning(request, '이용약관 및 개인정보처리방침에 동의해야 합니다.')
            return redirect('_register_modal.html')

        # 4. 기존 사용자 확인
        if User.objects.filter(username=username).exists():
            messages.warning(request, '이미 사용 중인 사용자 이름입니다.')
            return redirect('_register_modal.html')

        # 5. 새 사용자 생성 (create_user 사용)
        # User.objects.create_user() 사용: 비밀번호 해싱 및 저장을 자동으로 처리
        new_user = User.objects.create_user(
            username=username,
            password=password, # 원본 비밀번호 전달
            # --- 추가 필드 값 설정 ---
            cash = 1000000,
            portfolio_value = 1000000,
            level = 1,
            user_tier = "Bronze",
            real_cash = 0,  # 진짜 돈
            # otp_secret 설정 등 필요시 추가
        )
        # create_user는 객체를 생성하고 바로 save()까지 호출
        # 따라서 new_user.save() 를 별도로 호출할 필요가 없음

        messages.success(request, f'{username}님, 회원가IP 성공! 로그인해주세요.')
        return redirect('index')


    # POST 요청이 아닐 경우 (예: 직접 /register/ URL로 접근 시도)
    # 보통 회원가입 폼을 보여주는 GET 요청 처리가 필요하지만,
    # 모달 형태라면 그냥 메인 페이지로 보내는 것이 자연스러울 수 있습니다.
    return redirect('index')


from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required

@login_required
def profile(request):
    # 이 뷰 함수는 로그인된 사용자만 접근할 수 있도록
    return redirect('index')

@login_required
def profile222(request): # 함수 이름은 실제 사용하는 이름으로 변경
    user = request.user
    # ... (기존에 context 데이터를 만드는 로직) ...

    # --- ↓↓↓ ASI Coin 잔액 가져와서 context에 추가 ↓↓↓ ---
    asi_balance = user.asi_coin_balance
    # --- ↑↑↑ ASI Coin 잔액 가져와서 context에 추가 완료 ↑↑↑ ---

    context = {
        'user': user,
        # --- ↓↓↓ context 딕셔너리에 asi_balance 추가 ↓↓↓ ---
        'asi_balance': asi_balance,
        # --- ↑↑↑ context 딕셔너리에 asi_balance 추가 완료 ↑↑↑ ---
        # ... (기존 context 변수들) ...
    }
    # dashboard.html 템플릿 경로 확인 및 렌더링
    return render(request, 'main/dashboard.html', context)








import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST # POST 요청만 허용
from django.contrib.auth.decorators import login_required # 로그인된 사용자만 접근 허용
from django.views.decorators.csrf import csrf_exempt # 주의해서 사용하거나 클라이언트에서 CSRF 처리 필요
from django.contrib.auth import get_user_model # 또는 사용자 정의 User 모델 경로

# Holding/Trade 모델이 별도로 있다면 임포트
# from .models import Holding, Trade

User = get_user_model() # 현재 활성화된 User 모델 가져오기

@login_required # 로그인 필수 데코레이터
@require_POST   # POST 요청 필수 데코레이터
# @csrf_exempt # API 엔드포인트에 빠른 방법이지만, 보안상 취약함.
               # 더 나은 방법: Fetch 요청 시 CSRF 토큰 전송 (3단계 참조).
               # csrf_exempt 사용 시 다른 방식으로 CSRF 보호 필요.

def update_portfolio_api(request):
    """
    클라이언트로부터 포트폴리오 업데이트를 수신하여
    데이터베이스에 저장하는 API 엔드포인트.
    """
    try:
        # 1. 로그인된 사용자 가져오기
        user = request.user

        # 2. 클라이언트에서 보낸 JSON 데이터 파싱하기
        # 요청 본문이 비어있지 않은지 확인
        if not request.body:
            return JsonResponse({'status': 'error', 'message': '요청 본문이 비어있습니다.'}, status=400)

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': '잘못된 JSON 형식입니다.'}, status=400)

        # 3. 데이터 추출 (필요에 따라 유효성 검사 추가!)
        # 중요: 클라이언트 데이터를 그대로 신뢰하지 말고 검증하세요.
        # 예를 들어, 포트폴리오 가치는 가능하면 서버 측에서 재계산하세요.
        cash = data.get('cash')
        holdings_data = data.get('holdings', {}) # 보유 종목 딕셔너리 가져오기
        trades_data = data.get('trades', [])     # 거래 내역 리스트 가져오기 (새 거래만 보낼 수도 있음)
        level = data.get('level')
        user_tier = data.get('tier')
        real_cash = data.get('realCash')
        portfolio_value = data.get('portfolioValue') # 서버에서 재계산 고려

        # 4. 데이터베이스의 User 객체 업데이트하기
        # 기본 필드
        if cash is not None:
             # 유효성 검사 추가: cash가 유효한 숫자인지, 서버 로직과 맞는지 등 확인
            user.cash = cash
        if level is not None:
            user.level = level # user 모델에 'level' 필드가 있다고 가정
        if user_tier is not None:
            user.user_tier = user_tier # 'user_tier' 필드가 있다고 가정
        if real_cash is not None:
             # real_cash는 서버에서 엄격하게 관리하는 것이 좋음
             # user.real_cash = real_cash # 'real_cash' 필드가 있다고 가정
             pass # 또는 클라이언트 입력 대신 서버 로직 기반으로 업데이트
        if portfolio_value is not None:
             # 이상적으로는 서버에서 보유 종목과 현재가를 기반으로 재계산
             user.portfolio_value = portfolio_value # 'portfolio_value' 필드가 있다고 가정

        # --- 보유 종목 처리 (예시 방법) ---

        # 방법 A: User 모델에 'holdings_json'이라는 JSONField 사용
        # user.holdings_json = holdings_data # 딕셔너리를 JSON으로 직접 저장

        # 방법 B: 별도의 Holding 모델 사용
        # 더 복잡한 로직 필요:
        # - DB에서 해당 유저의 기존 보유 종목 가져오기.
        # - 클라이언트의 holdings_data와 비교하기.
        # - 새 Holding 객체 생성, 기존 객체 업데이트, 없어진 객체 삭제.
        # 예시 (개념적 - Holding 모델 필요):
        # existing_symbols = {h.symbol for h in user.holding_set.all()}
        # current_symbols = set(holdings_data.keys())
        # # 보유 종목 추가/업데이트
        # for symbol, details in holdings_data.items():
        #     Holding.objects.update_or_create(
        #         user=user,
        #         symbol=symbol,
        #         defaults={'quantity': details.get('quantity'), 'avg_price': details.get('avgPrice')}
        #     )
        # # 더 이상 없는 보유 종목 삭제
        # user.holding_set.filter(symbol__in=(existing_symbols - current_symbols)).delete()

        # --- 거래 내역 처리 (예시 방법) ---
        # 보통 클라이언트에서는 전체 리스트 대신 *새로운* 거래만 보냅니다.
        # 만약 새로운 거래가 `data`에 포함되어 있다면:
        # new_trade_info = data.get('new_trade') # 클라이언트가 새 거래 정보를 보낸다고 가정
        # if new_trade_info:
        #     Trade.objects.create(
        #         user=user,
        #         symbol=new_trade_info.get('symbol'),
        #         trade_type=new_trade_info.get('type'), # 'buy' 또는 'sell'
        #         quantity=new_trade_info.get('quantity'),
        #         price=new_trade_info.get('price'),
        #         timestamp=new_trade_info.get('timestamp') # 서버에서 설정하는 것이 이상적
        #     )

        # 5. 변경 사항 저장하기
        user.save()

        # 6. 성공 응답 반환하기
        return JsonResponse({'status': 'success', 'message': '포트폴리오가 성공적으로 업데이트되었습니다.'})

    except Exception as e:
        # 디버깅을 위해 에러 로그 남기기
        print(f"사용자 {request.user.username}의 포트폴리오 업데이트 중 오류 발생: {e}")
        # 일반적인 에러 응답 반환하기
        return JsonResponse({'status': 'error', 'message': f'내부 서버 오류가 발생했습니다: {e}'}, status=500)




































import requests
import json
from django.conf import settings
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
# --- !!! 경고: 절대 경로 사용 !!! ---
PARAMS_FILE_PATH = r"D:\AI_pycharm\pythonProject\3_AI_LLM_finance\a_korea_invest_api_env\secret_data\params.py"
# ------------------------------------

KIS_APP_KEY = None
KIS_APP_SECRET = None
# 실제 KIS API URL (실전투자 기준 - KIS 문서에서 재확인 필요)
KIS_BASE_URL = "https://openapi.koreainvestment.com:9443"

# --- 파일에서 API 키 읽어오기 ---
try:
    print(f"절대 경로에서 KIS 키 로딩 시도: {PARAMS_FILE_PATH}")
    # params.py 파일 형식 가정: 각 줄에 '변수명 = "값"' 형태
    with open(PARAMS_FILE_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith("stock_API_key"):
                line = line.replace(' ', '')
                parts = line.split('key=')
                KIS_APP_KEY = parts[1].strip().strip('"').strip("'")

            elif line.startswith("stock_Secret_key"): # App Secret 변수명도 params.py에 있다고 가정
                line = line.replace(' ','')
                parts = line.split('key=')
                KIS_APP_SECRET = parts[1].strip().strip('"').strip("'")
            # 필요한 다른 키가 있다면 elif 추가

except FileNotFoundError:
    print(f"!!! 치명적 오류: 지정된 절대 경로에 params.py 파일이 없습니다: {PARAMS_FILE_PATH} !!!")
    # 이 경우 애플리케이션 실행이 불가능할 수 있음
    KIS_APP_KEY = None # None으로 설정하여 이후 함수에서 처리
    KIS_APP_SECRET = None

except Exception as e:
    print(f"!!! 치명적 오류: {PARAMS_FILE_PATH} 파일 읽기/파싱 중 예외 발생: {e} !!!")
    KIS_APP_KEY = None
    KIS_APP_SECRET = None

# --- 웹소켓 접속키 발급 함수 ---
def get_kis_approval_key():
    """KIS REST API를 호출하여 임시 웹소켓 접속키(approval_key)를 발급받습니다."""
    if not KIS_APP_KEY or not KIS_APP_SECRET:
        print("오류: KIS App Key 또는 Secret 값이 없어 approval_key를 발급할 수 없습니다.")
        return None

    path = "/oauth2/Approval"
    url = f"{KIS_BASE_URL}{path}"
    headers = {"content-type": "application/json"}
    # params.py에서 읽어온 키 사용
    body = {
        "grant_type": "client_credentials",
        "appkey": KIS_APP_KEY,
        "secretkey": KIS_APP_SECRET # KIS 문서 따라 'secretkey' 또는 'appsecret' 확인
    }
    print(f"KIS Approval Key 요청 URL: {url}")

    try:
        response = requests.post(url, headers=headers, data=json.dumps(body), timeout=10) # 타임아웃 증가
        response.raise_for_status() # 오류 시 예외 발생
        data = response.json()
        approval_key = data.get('approval_key')
        if approval_key:
            print("KIS Approval Key 발급 성공.")
            return approval_key
        else:
            print(f"오류: KIS 응답에서 'approval_key'를 찾을 수 없음: {data}")
            return None
    except requests.exceptions.Timeout:
        print(f"오류: KIS Approval API 요청 시간 초과 ({url})")
        return None
    except requests.exceptions.RequestException as e:
        print(f"오류: KIS Approval API 요청 실패: {e}")
        if e.response is not None:
            print(f"응답 코드: {e.response.status_code}")
            try:
                error_data = e.response.json()
                print(f"오류 응답 내용 (JSON): {error_data}")
            except json.JSONDecodeError:
                print(f"오류 응답 내용 (Text): {e.response.text}")
        return None
    except json.JSONDecodeError as e:
         print(f"오류: KIS Approval API JSON 응답 파싱 실패: {e}")
         print(f"수신된 응답 내용: {response.text}")
         return None



def web_socket_API(request): # 함수 이름은 실제 사용하는 이름으로 변경
    print("index2_simulator_view 실행됨. 웹소켓 키 발급 시도...")
    # 1. 뷰 함수 내부에서 키 발급 함수 호출
    websocket_approval_key =  get_kis_approval_key() #웹소켓 API호출

    if not websocket_approval_key:
        print("!!! 웹소켓 키 발급 실패 !!!")
        # 키 발급 실패 시 처리 (예: 에러 메시지 전달)
        # websocket_approval_key = "" # 빈 값으로 설정

    # 2. 템플릿에 전달할 context 데이터 생성
    context = {
        'user': request.user,
        # ★ 발급받은 키(또는 빈 문자열)를 컨텍스트에 추가
        'websocket_approval_key': websocket_approval_key or "",
        # ... 다른 필요한 데이터 추가 ...
    }
    return render(request, 'main/index2_simulator.html', context)



















###############아이템구매

from django.http import JsonResponse
from django.views.decorators.http import require_POST # POST 요청만 받도록
from django.views.decorators.csrf import csrf_exempt # 필요시 CSRF 예외 처리 (JS에서 토큰 보내는것 권장)
from django.contrib.auth.decorators import login_required # 로그인 필수
import json
from decimal import Decimal, InvalidOperation
from django.utils import timezone
from datetime import timedelta
from django.db import transaction
from django.db.models import F # DB 업데이트 시 원자적 연산 지원
from django.contrib.auth import get_user_model

# --- ★★★ 서비스 함수 및 모델 Import (실제 경로로 수정 필수!) ★★★ ---
# spend_asi_coin 함수가 정의된 파일 경로에서 import
# 예: from chart.blockchain_reward import spend_asi_coin
from chart.blockchain_reward import spend_asi_coin # 사용자가 chart 폴더 언급했으므로 임시 적용

# User 모델 및 구독 모델 import (main 앱의 models.py 에 있다고 가정)
# User는 get_user_model() 사용, 구독 모델은 .models 에서 가져오기
from main.models import StrategyPageSubscription, PositionViewSubscription

User = get_user_model()
# --------------------------------------------------------------------

@login_required
@require_POST
@csrf_exempt # JavaScript에서 CSRF 토큰을 헤더에 포함하여 보내는 경우 이 줄은 주석 처리하거나 삭제
def purchase_item_api_view(request):
    """
    ASI Coin 상점 아이템 구매 요청을 처리하고,
    (필요시) 코인 차감 성공 시 각 아이템의 효과를 적용하는 API 뷰. (가격 0 처리 포함)
    """
    print("\n[DEBUG] ===== purchase_item_api_view 시작 =====")
    try:
        # 요청 본문에서 JSON 데이터 파싱
        data = json.loads(request.body)
        item_id = data.get('item_id') # 프론트엔드에서 보낸 구매할 아이템의 ID
        user = request.user         # 요청을 보낸 로그인된 사용자
        user_id = user.id

        # 아이템 정보 (가격, 이름 등) - DB나 설정 파일 권장
        # ★★★ 무료 아이템은 가격을 Decimal("0") 으로 설정 ★★★
        items_info = {
            'cash_refill': {'price': Decimal("0"), 'name': "머니 충전"},
            'level_xp_1000': {'price': Decimal("0"), 'name': "레벨 경험치 +1000"},
            'nickname_color': {'price': Decimal("0"), 'name': "닉네임 색상 변경권"},
            'view_trader': {'price': Decimal("0"), 'name': "트레이더 포지션 보기 (1주일)"},
            'strategy_page_sub': {'price': Decimal("0"), 'name': "전략 페이지 접근권 (1주일)"},
            'auto_trade_10h': {'price': Decimal("0"), 'name': "자동매매 시간 충전 (10시간)"},
            # 'free_sample': {'price': Decimal("0"), 'name': "무료 샘플"}, # 가격 0 예시
        }

        # 요청된 item_id 유효성 확인
        if item_id not in items_info:
             return JsonResponse({'success': False, 'message': '알 수 없는 아이템입니다.'}, status=400)

        item_info = items_info[item_id]
        item_price = item_info['price'] # Decimal 타입 가격
        item_name = item_info['name']

        # --- 가격 확인 및 코인 사용(필요시) / 효과 적용 진행 여부 결정 ---
        proceed_to_action = False # 효과 적용 단계 진행 플래그

        if item_price == Decimal("0"):
            # 가격 0 (무료): 코인 차감 없이 바로 진행
            print(f"로그: 아이템 '{item_name}' (ID: {item_id}) - 무료 아이템")
            proceed_to_action = True
        elif item_price > Decimal("0"):
            # 가격 > 0 (유료): 코인 사용(차감) 시도
            print(f"로그: 아이템 '{item_name}' (ID: {item_id}) - {item_price} ASI 차감 시도.")
            if spend_asi_coin(user_id, item_price, item_name):
                print(f"로그: 사용자 {user_id} 코인 차감 성공.")
                proceed_to_action = True # 코인 차감 성공
            else:
                # spend_asi_coin 실패 (잔액 부족 등)
                print(f"로그: 사용자 {user_id} 코인 차감 실패 (잔액 부족 등).")
                return JsonResponse({'success': False, 'message': '코인 잔액이 부족하거나 코인 사용 중 오류가 발생했습니다.'}, status=400)
        else:
             # 가격 < 0 (오류)
             print(f"오류: 아이템 '{item_name}' (ID: {item_id}) 가격 음수: {item_price}")
             return JsonResponse({'success': False, 'message': '아이템 가격이 유효하지 않습니다.'}, status=500)

        print(f"[DEBUG] 아이템 효과 적용 단계 진입 직전, proceed_to_action = {proceed_to_action}")

        # --- 아이템 효과 적용 (proceed_to_action 이 True 일 때만) ---
        if proceed_to_action:
            action_success = False # 효과 적용 성공 플래그
            result_message = ""    # 성공 메시지

            try:
                # DB 업데이트 관련 로직은 트랜잭션으로 묶어 원자성 보장
                with transaction.atomic():
                    # 최신 사용자 정보 로드 (락 설정)
                    user = User.objects.select_for_update().get(pk=user_id)

                    # --- 각 아이템 ID 별 효과 처리 ---
                    if item_id == 'cash_refill':
                        user.cash = 1000000.0
                        user.save(update_fields=['cash'])
                        action_success = True
                        result_message = "모의투자 머니가 1,000,000으로 초기화되었습니다."

                    elif item_id == 'level_xp_1000':
                        user.level_xp = F('level_xp') + 1000.0
                        user.save(update_fields=['level_xp'])
                        action_success = True
                        result_message = "레벨 경험치 1000이 추가되었습니다."
                        # TODO: 레벨업 로직 호출

                    elif item_id == 'nickname_color':
                        selected_color = data.get('color') # ★ JS에서 전달 필요 ★
                        if not selected_color or not isinstance(selected_color, str) or not selected_color.startswith('#') or len(selected_color) != 7:
                            raise ValueError("올바른 색상 코드(#RRGGBB)가 필요합니다.")
                        user.nickname_color = selected_color
                        user.save(update_fields=['nickname_color'])
                        action_success = True
                        result_message = f"닉네임 색상이 {selected_color}로 변경되었습니다."

                    elif item_id == 'strategy_page_sub':
                        # TODO: 중복/연장 정책 구현 가능성
                        StrategyPageSubscription.objects.create(subscriber=user)
                        action_success = True
                        result_message = "전략 페이지 접근권(7일)이 활성화되었습니다."

                    elif item_id == 'view_trader':
                        target_user_id = data.get('target_user_id') # ★ JS에서 전달 필요 ★
                        if not target_user_id: raise ValueError("구독 대상 트레이더 ID가 필요합니다.")
                        try:
                            target_trader = User.objects.get(pk=target_user_id, position_sharing_enabled=True)
                            if user.id == target_trader.id: raise ValueError("자기 자신을 구독할 수 없습니다.")
                            # TODO: 중복/연장 정책 구현 가능성
                            PositionViewSubscription.objects.create(subscriber=user, target_trader=target_trader)
                            action_success = True
                            result_message = f"{target_trader.username}님 포지션 구독(7일)이 시작되었습니다."
                        except User.DoesNotExist:
                            raise ValueError("구독 대상 트레이더를 찾을 수 없거나 비공개 상태입니다.")

                    elif item_id == 'auto_trade_10h':
                        seconds_to_add = 10 * 60 * 60
                        user.auto_trade_seconds_remaining = F('auto_trade_seconds_remaining') + seconds_to_add
                        user.save(update_fields=['auto_trade_seconds_remaining'])
                        action_success = True
                        user.refresh_from_db() # 시간 표시 위해
                        result_message = f"자동매매 시간이 10시간 충전되었습니다. (현재 약 {user.auto_trade_seconds_remaining // 3600} 시간)"

                    else:
                         # items_info에는 있지만 로직이 없는 경우 (개발 중 실수)
                         raise NotImplementedError(f"아이템 ID '{item_id}' 효과 처리 로직이 없습니다.")

                # --- 최종 결과 반환 (아이템 효과 적용 결과 기준) ---
                if action_success:
                     user.refresh_from_db() # 최종 DB 잔액 확인 위해
                     return JsonResponse({
                         'success': True,
                         'message': result_message or f"'{item_name}' 구매/획득/사용 완료!",
                         'new_balance': user.asi_coin_balance # 프론트엔드 잔액 업데이트용
                     })
                else:
                     # 위 로직 문제로 action_success가 설정 안 된 경우 등
                     # transaction.atomic에 의해 롤백됨
                     return JsonResponse({'success': False, 'message': '아이템 효과 적용에 실패했습니다.'}, status=500) # 서버 내부 오류

            except Exception as e: # 아이템 효과 적용 중 예외 발생 (ValueError, DB Error 등)
                print(f"오류: 아이템 효과 적용 실패 ({item_id}) - {e}")
                # transaction.atomic 이 DB 변경사항 롤백
                return JsonResponse({'success': False, 'message': f"'{item_name}' 효과 적용 중 오류 발생: {e}"}, status=500)
        # proceed_to_action 이 False인 경우는 이미 위에서 처리됨

    # --- 최외곽 에러 처리 ---
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': '잘못된 요청 형식입니다.'}, status=400)
    except Exception as e:
        print(f"API 오류 (/api/shop/purchase/): {e}") # 상세 오류 서버 로그에 기록
        return JsonResponse({'success': False, 'message': '서버 내부 오류가 발생했습니다.'}, status=500)















from django.http import JsonResponse
from django.views.decorators.http import require_POST # POST 요청만 받도록
from django.views.decorators.csrf import ensure_csrf_cookie # CSRF 처리 관련 (필요시)
from django.contrib.auth.decorators import login_required
from chart.blockchain_reward import process_trade_result

@login_required # 로그인 필수
@require_POST  # POST 요청만 허용
# @ensure_csrf_cookie # CSRF 쿠키 보장 (필요에 따라)
def process_trade_result_api_view(request):
    """ JavaScript로부터 매도 결과를 받아 서비스 함수를 호출하는 API 뷰 """
    try:
        # 요청 본문(body)에서 JSON 데이터 읽기
        data = json.loads(request.body)
        profit_usd = data.get('profit') # JavaScript에서 보낸 'profit' 키의 값
        user_id = request.user.id

        # profit 값이 숫자인지 확인 (간단한 유효성 검사)
        if profit_usd is None or not isinstance(profit_usd, (int, float)):
            return JsonResponse({'success': False, 'message': '유효한 수익 정보(profit)가 필요합니다.'}, status=400)

        # 서비스 함수 호출하여 DB 업데이트 시도
        success = process_trade_result(user_id, float(profit_usd))

        if success:
            # 성공 시
            return JsonResponse({'success': True, 'message': '매도 결과가 처리되었습니다.'})
        else:
            # 서비스 함수 내부에서 실패한 경우 (예: 사용자 없음, DB 오류 등)
            # process_trade_result 함수 내부의 print 로그로 원인 파악 필요
            return JsonResponse({'success': False, 'message': '매도 결과 처리 중 서버 내부 오류가 발생했습니다.'}, status=500)

    except json.JSONDecodeError:
        # 요청 본문이 유효한 JSON이 아닐 경우
        return JsonResponse({'success': False, 'message': '잘못된 요청 형식입니다 (JSON 오류).'}, status=400)
    except Exception as e:
        # 기타 예외 처리
        print(f"API 오류: /api/trade/process_result/ - {e}") # 서버 로그에 기록
        return JsonResponse({'success': False, 'message': '서버 내부 오류가 발생했습니다.'}, status=500)


















# 예시: your_app_name/views.py

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
import json
from decimal import Decimal, InvalidOperation # Decimal 및 오류 처리 import

# initiate_onchain_withdrawal 함수 import (★ 실제 경로 확인 및 수정 필요 ★)
# 예: from your_project_name.blockchain_service import initiate_onchain_withdrawal
from chart.blockchain_service import initiate_onchain_withdrawal # 임시 경로

@login_required # 로그인 필수
@require_POST  # POST 요청만 허용
# @csrf_exempt # CSRF 테스트 필요 시 임시 사용, 실제로는 JS에서 토큰 전송 필요
def initiate_withdrawal_api_view(request):
    """ 사용자의 ASI Coin 온체인 출금 요청을 처리하는 API 뷰 """
    try:
        # 1. 요청 데이터 파싱
        data = json.loads(request.body)
        # JavaScript에서 'amount' 키로 출금 금액(문자열 또는 숫자)을 보냈다고 가정
        amount_str = data.get('amount')
        user_id = request.user.id

        # 2. 입력값 유효성 검증
        if amount_str is None:
            return JsonResponse({'success': False, 'message': '출금할 금액(amount)이 요청에 포함되지 않았습니다.'}, status=400)

        try:
            amount_to_withdraw = Decimal(amount_str)
            if amount_to_withdraw <= 0:
                raise ValueError("출금 금액은 0보다 커야 합니다.")
        except (ValueError, InvalidOperation):
             return JsonResponse({'success': False, 'message': '출금 금액이 올바른 숫자 형식이 아닙니다.'}, status=400)

        # 3. 핵심 서비스 함수 호출
        # initiate_onchain_withdrawal 함수는 {'success': True/False, 'tx_hash': '...', 'message': '...'} 형태의 dict를 반환한다고 가정
        result = initiate_onchain_withdrawal(user_id, amount_to_withdraw)

        # 4. 서비스 함수 결과에 따라 최종 응답 반환
        if result.get('success'):
            # 성공 시 (tx_hash 포함)
            return JsonResponse(result)
        else:
            # 실패 시 (message 포함)
            # 실패 원인(잔액 부족, 주소 미등록 등)에 따라 status code를 다르게 주는 것이 좋음 (여기서는 400으로 통일)
            return JsonResponse(result, status=400)

    except json.JSONDecodeError:
        # 요청 본문이 JSON이 아닐 경우
        return JsonResponse({'success': False, 'message': '잘못된 요청 형식입니다 (JSON 오류).'}, status=400)
    except Exception as e:
        # 기타 예상치 못한 서버 오류
        print(f"API 오류: /api/wallet/withdraw/ - {e}") # 서버 로그에 기록
        return JsonResponse({'success': False, 'message': '서버 내부 오류가 발생했습니다.'}, status=500)















