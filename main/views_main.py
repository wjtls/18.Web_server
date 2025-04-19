from django.shortcuts import render
from django.http import HttpResponse
import requests
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate # 자동 로그인을 위해 login 추가
from django.contrib import messages # 사용자에게 피드백 메시지를 보여주기 위함


def index(request):
    return render(request,"main/index_homepage.html")

def index2_simulator(request):
    return render(request,"main/index2_simulator.html")

def index3_strategy(request):
    return render(request,"main/index3_strategy.html")

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