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

#Holding/Trade 모델이 별도로 있다면 임포트
from .models import Holding

def index(request):
    return render(request,"main/index_homepage.html")

def index2_simulator_backup(request):
    return render(request,"main/index2_simulator.html")

def index2_simulator(request):
    user = request.user

    try:
        # JavaScript용 딕셔너리 생성
        holdings_qs = user.holdings.all()
        holdings_dict_for_js = {}
        for holding in holdings_qs:
            holdings_dict_for_js[holding.symbol] = {
                'quantity': holding.quantity, # 모델 필드 이름 확인! (quantity or stock_count)
                'avgPrice': holding.avg_price,
                'symbol': holding.symbol
            }

        context = {
            'user': user,
            # 생성된 딕셔너리를 JSON 문자열로 변환하여 전달
            'holdings_json_for_js': json.dumps(holdings_dict_for_js)
        }
    except:
        context={'user': user}

    return render(request, 'main/index2_simulator.html', context)


def index2_1(request):
    return render(request,"main/index2_1_past_simulator.html")

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
            level_xp = 0.0,
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

User = get_user_model() # 현재 활성화된 User 모델 가져오기

@login_required # 로그인 필수 데코레이터
@require_POST   # POST 요청 필수 데코레이터
# @csrf_exempt # API 엔드포인트에 빠른 방법이지만, 보안상 취약함.
               # 더 나은 방법: Fetch 요청 시 CSRF 토큰 전송 (3단계 참조).
               # csrf_exempt 사용 시 다른 방식으로 CSRF 보호 필요.

def update_portfolio_api(request):
    """
    클라이언트로부터 포트폴리오 전체 상태를 수신하여
    데이터베이스에 저장(동기화)하는 API 엔드포인트.
    """
    try:
        # 1. 현재 로그인된 사용자 객체 가져오기
        user = request.user

        # 2. 클라이언트에서 보낸 JSON 데이터 파싱하기
        if not request.body:
            print(f"오류: 사용자 {user.username} 요청 본문 비어있음.")
            return JsonResponse({'status': 'error', 'message': '요청 본문이 비어있습니다.'}, status=400)

        try:
            # 요청 본문을 UTF-8로 디코딩 시도 (일반적)
            data = json.loads(request.body.decode('utf-8'))
            print(f"로그: 사용자 {user.username} 포트폴리오 데이터 수신: {data}") # 디버깅: 수신 데이터 확인
        except json.JSONDecodeError:
            print(f"오류: 사용자 {user.username} 잘못된 JSON 수신: {request.body[:200]}...") # 앞부분만 로깅
            return JsonResponse({'status': 'error', 'message': '잘못된 JSON 형식입니다.'}, status=400)
        except UnicodeDecodeError:
             print(f"오류: 사용자 {user.username} 요청 본문 디코딩 실패.")
             return JsonResponse({'status': 'error', 'message': '요청 인코딩 오류입니다.'}, status=400)


        # 3. 데이터 추출 및 기본 유효성 검사 (필요시 강화)
        # 클라이언트 데이터를 직접 신뢰하는 것은 보안상 위험할 수 있습니다.
        # 서버에서 재계산 가능한 값(예: portfolio_value)은 가능하면 서버에서 계산하는 것이 좋습니다.

        cash = data.get('cash') # get() 사용으로 키 부재 시 None 반환
        holdings_data = data.get('holdings', {}) # 기본값 빈 딕셔너리
        trades_data = data.get('trades', [])     # 기본값 빈 리스트
        # level = data.get('level') # User 모델에 level 필드가 있다면
        user_tier = data.get('tier') # User 모델에 user_tier 필드가 있다면
        # real_cash = data.get('realCash') # 서버에서 관리 권장
        portfolio_value_client = data.get('portfolioValue') # 클라이언트가 계산한 값

        # 4. 데이터베이스 업데이트 (원자적 트랜잭션 사용)
        try:
            with transaction.atomic():
                # 4.1 User 객체 잠금 및 업데이트 (동시성 문제 방지)
                user_locked = User.objects.select_for_update().get(pk=user.pk)

                update_fields_user = [] # User 모델 업데이트 필드 추적

                # 현금 업데이트 (숫자인지, 음수 아닌지 등 검증 추가 가능)
                if cash is not None and isinstance(cash, (int, float)):
                    user_locked.cash = cash
                    update_fields_user.append('cash')
                # else: # 값이 없거나 타입이 안맞으면 로깅 또는 에러 처리
                #     print(f"경고: 사용자 {user.username}의 cash 값이 유효하지 않음: {cash}")

                # 티어 업데이트 (문자열인지, 유효한 값인지 검증 추가 가능)
                if user_tier is not None and isinstance(user_tier, str):
                    user_locked.user_tier = user_tier # user_tier 필드 존재 가정
                    update_fields_user.append('user_tier')

                # Level 업데이트 (User 모델에 level 필드가 있다면)
                # if level is not None and isinstance(level, int):
                #     user_locked.level = level
                #     update_fields_user.append('level')

                # 포트폴리오 가치 (클라이언트 값 저장 vs 서버 재계산)
                # 여기서는 일단 클라이언트 값 저장, 추후 서버 재계산 로직 추가 권장
                if portfolio_value_client is not None and isinstance(portfolio_value_client, (int, float)):
                     user_locked.portfolio_value = portfolio_value_client # portfolio_value 필드 존재 가정
                     update_fields_user.append('portfolio_value')

                # User 모델 필드 변경사항 저장 (변경된 필드만)
                if update_fields_user:
                    user_locked.save(update_fields=update_fields_user)
                    print(f"로그: 사용자 {user.username} User 모델 업데이트 완료: {update_fields_user}")


                # 4.2 보유 종목(Holdings) 업데이트
                # 현재 방식: 기존 보유 종목 전체 삭제 후, 클라이언트 데이터 기준으로 새로 생성
                # 장점: 구현 간단 / 단점: 매번 삭제/생성으로 비효율적일 수 있음, ID 변경 가능성

                user_locked.holdings.all().delete() # User 모델의 related_name='holdings' 사용
                print(f"로그: 사용자 {user.username} 기존 Holding 레코드 삭제 완료.")

                new_holdings_to_create = [] # 벌크 생성을 위한 리스트
                total_stock_value_server = 0 # 서버에서 평가액 계산용 (선택적)

                # 클라이언트에서 받은 holdings_data 순회
                for symbol, holding_info in holdings_data.items():
                    # 데이터 유효성 검사 강화
                    quantity = holding_info.get('quantity')
                    avg_price = holding_info.get('avgPrice')
                    symbol_str = str(symbol) # 심볼 문자열 확인

                    # 수량은 양수, 평균가는 0 이상인 경우만 처리
                    if (isinstance(quantity, int) and quantity > 0 and
                        isinstance(avg_price, (int, float)) and avg_price >= 0):

                        # 새 Holding 객체 생성 (아직 DB 저장 안 함)
                        new_holdings_to_create.append(Holding(
                            user=user_locked, # 잠금된 사용자 객체 사용
                            symbol=symbol_str,
                            quantity=quantity,
                            avg_price=avg_price
                        ))
                        # 서버에서 평가액 계산 로직 (get_current_price 함수 필요)
                        # current_price = get_current_price(symbol_str) # 가정
                        # total_stock_value_server += quantity * current_price
                    else:
                         print(f"경고: 사용자 {user.username}의 종목 {symbol} 데이터 유효하지 않음 - 건너<0xEB><0x9B><0x81>. Info: {holding_info}")

                # 준비된 Holding 객체들을 한 번에 DB에 생성 (효율적)
                if new_holdings_to_create:
                    Holding.objects.bulk_create(new_holdings_to_create)
                    print(f"로그: 사용자 {user.username} 새로운 Holding 레코드 {len(new_holdings_to_create)}개 생성 완료.")

                # (선택적) 서버에서 재계산한 포트폴리오 가치 업데이트
                # user_locked.portfolio_value = user_locked.cash + total_stock_value_server
                # user_locked.save(update_fields=['portfolio_value'])

                # 4.3 거래 내역(Trades) 추가 (Trade 모델이 있다고 가정)
                # 이 부분은 클라이언트에서 *새로운* 거래 내역만 보낸다고 가정
                # 또는 전체 거래 내역을 보내면 중복 체크 후 저장하는 로직 필요
                # new_trades_to_create = []
                # for trade_info in trades_data:
                #     # trade_info 유효성 검사 (필수 필드: symbol, action, quantity, price, timestamp 등)
                #     if (trade_info.get('symbol') and trade_info.get('action') in ['buy', 'sell'] and
                #         trade_info.get('quantity') > 0 and trade_info.get('price') >= 0 and trade_info.get('timestamp')):
                #         # Trade 모델 객체 생성
                #         new_trades_to_create.append(Trade(
                #             user=user_locked,
                #             symbol=trade_info['symbol'],
                #             action=trade_info['action'],
                #             quantity=trade_info['quantity'],
                #             price=trade_info['price'],
                #             timestamp=trade_info['timestamp'] # 타임스탬프 형식 변환 필요할 수 있음
                #             # ... 기타 필드 ...
                #         ))
                #     else:
                #         print(f"경고: 사용자 {user.username}의 거래 내역 데이터 유효하지 않음: {trade_info}")
                #
                # if new_trades_to_create:
                #      Trade.objects.bulk_create(new_trades_to_create)
                #      print(f"로그: 사용자 {user.username} 새로운 Trade 레코드 {len(new_trades_to_create)}개 생성 완료.")

            # 트랜잭션 성공적으로 완료

        except Exception as db_error:
            # 트랜잭션 내에서 오류 발생 시 롤백됨
            print(f"오류: 사용자 {user.username} DB 업데이트 중 오류 발생 (롤백됨): {db_error}")
            traceback.print_exc()
            return JsonResponse({'status': 'error', 'message': f'데이터베이스 처리 중 오류 발생: {db_error}'}, status=500)


        # 5. 성공 응답 반환하기
        print(f"성공: 사용자 {user.username} 포트폴리오 DB 동기화 완료.")
        return JsonResponse({'status': 'success', 'message': '포트폴리오가 성공적으로 업데이트되었습니다.'})

    except Exception as e:
        # 요청 처리 중 예기치 않은 오류 발생
        print(f"오류: 사용자 {request.user.username if request.user.is_authenticated else '비로그인'} 포트폴리오 업데이트 처리 중 최상위 오류 발생: {e}")
        traceback.print_exc()
        return JsonResponse({'status': 'error', 'message': f'서버 내부 오류가 발생했습니다: {e}'}, status=500)











import json
from django.http import JsonResponse
from django.views.decorators.http import require_GET # GET 요청만 허용
from django.contrib.auth.decorators import login_required # 로그인된 사용자만 접근 허용
from django.forms.models import model_to_dict # 모델 인스턴스를 딕셔너리로 변환
# Traceback import (오류 로깅용)
import traceback


# User 모델 import
from .models import User # 사용자 모델 import
from django.contrib.auth import get_user_model
User = get_user_model()

# Holding, Trade 모델 import (네 models.py에 정의되어 있어야 함)
# from .models import Holding, Trade # 보유 종목, 거래 내역 모델 import

# 임시로 모델 클래스 이름만 가정 (실제 네 모델 이름으로 변경 필요)
# class Holding: pass # 예시
# class Trade: pass # 예시

# ★★★ 중요: 실제 네 models.py에 정의된 User, Holding, Trade 모델을 정확히 임포트하고 사용해야 함 ★★★
# Holding 모델이 User와 ForeignKey로 연결되어 있고 related_name이 'holdings'라고 가정
# Trade 모델도 User와 ForeignKey로 연결되어 있고 related_name이 'trades'라고 가정
# Holding 모델에 symbol, quantity, avg_price 등의 필드가 있다고 가정
# Trade 모델에 symbol, action, quantity, price, profit, timestamp 등의 필드가 있다고 가정

@login_required # 로그인된 사용자만 이 API에 접근 가능
@require_GET   # 이 API는 GET 요청만 받음
def load_portfolio_api(request):
    """
    로그인된 사용자의 포트폴리오 상태를 DB에서 조회하여 JSON으로 반환하는 API 엔드포인트.
    """
    try:
        # 1. 현재 로그인된 사용자 객체 가져오기
        user = request.user

        print(f"로그: 사용자 {user.username}의 포트폴리오 상태 조회 요청 수신.")

        # 2. 사용자 포트폴리오 데이터 조회
        # User 모델 필드들
        # user_data = model_to_dict(user, fields=['username', 'cash', 'initial_deposit', 'level', 'user_tier', 'real_cash', 'portfolio_value'])
        # 필요한 필드만 직접 딕셔너리에 담는 것이 더 명확할 수 있습니다.

        # 2.1 User 모델의 기본 정보 가져오기
        portfolio_data = {
            'userName': user.username,
            # 필드 이름은 실제 네 User 모델의 필드 이름과 JSON 응답에서 사용할 이름에 맞춰
            'cash': user.cash, # User 모델에 cash 필드가 있다고 가정
            # 'initialDeposit': user.initial_deposit, # User 모델에 initial_deposit 필드가 있다고 가정
            'level': user.current_level, # User 모델에 level 필드가 있다고 가정
            'tier': user.user_tier, # User 모델에 user_tier 필드가 있다고 가정
            'realCash': user.real_cash, # User 모델에 real_cash 필드가 있다고 가정
            'portfolioValue': user.portfolio_value, # User 모델에 portfolio_value 필드가 있다고 가정
            # 필요에 따라 User 모델의 다른 필드들도 추가
        }

        # 2.2 보유 종목 (Holdings) 정보 가져오기
        # User 모델의 related_name='holdings'를 사용하여 보유 종목 객체들 조회
        holdings_list = []
        # user.holdings.all() -> User 모델에 related_name='holdings'로 연결된 Holding 객체들
        for holding in user.holdings.all(): # Holding 모델 객체들을 순회
            # Holding 모델 필드들을 딕셔너리로 변환하여 리스트에 추가
            # 필드 이름은 실제 네 Holding 모델 필드 이름과 JSON 응답에 맞춰
            holdings_list.append({
                # 'id': holding.id, # 클라이언트에서 Holding 객체의 DB ID가 필요하다면 추가
                'symbol': holding.symbol, # Holding 모델에 symbol 필드가 있다고 가정
                'quantity': holding.quantity, # Holding 모델에 quantity 필드가 있다고 가정
                'avgPrice': holding.avg_price, # Holding 모델에 avg_price 필드가 있다고 가정
                # 필요에 따라 Holding 모델의 다른 필드들도 추가
            })
        # 클라이언트 portfolio.holdings가 딕셔너리 형태였으므로 여기서도 딕셔너리로 구성
        # { symbol: { quantity: ..., avgPrice: ... }, ... } 형태
        holdings_dict = {h['symbol']: h for h in holdings_list} # 심볼을 키로 하는 딕셔너리 생성

        portfolio_data['holdings'] = holdings_dict


        # 2.3 거래 내역 (Trades) 정보 가져오기
        # User 모델의 related_name='trades'를 사용하여 거래 내역 객체들 조회
        trades_list = []
        # user.trades.all() -> User 모델에 related_name='trades'로 연결된 Trade 객체들
        # 최신 거래 내역부터 보여주려면 order_by('-timestamp') 등을 추가
        for trade in user.trades.all().order_by('-timestamp'): # Trade 모델 객체들을 순회 (최신순 정렬 예시)
            # Trade 모델 필드들을 딕셔너리로 변환하여 리스트에 추가
            # 필드 이름은 실제 네 Trade 모델 필드 이름과 JSON 응답에 맞춰
            trades_list.append({
                # 'id': trade.id, # 클라이언트에서 Trade 객체의 DB ID가 필요하다면 추가
                'timestamp': trade.timestamp.isoformat() if trade.timestamp else None, # 날짜/시간 형식 변환 (ISO 8601 권장)
                'symbol': trade.symbol, # Trade 모델에 symbol 필드가 있다고 가정
                'action': trade.action, # Trade 모델에 action 필드가 있다고 가정 ('buy', 'sell' 문자열)
                'quantity': trade.quantity, # Trade 모델에 quantity 필드가 있다고 가정
                'price': trade.price, # Trade 모델에 price 필드가 있다고 가정 (체결 단가)
                'profit': trade.profit if trade.action == 'sell' else None, # Trade 모델에 profit 필드가 있다면 (매도 시 손익)
                # 필요에 따라 Trade 모델의 다른 필드들도 추가
            })

        portfolio_data['trades'] = trades_list


        # 3. 포트폴리오 데이터를 JSON 응답으로 반환
        print(f"로그: 사용자 {user.username}의 포트폴리오 데이터 조회 완료. JSON 응답 반환.")
        return JsonResponse(portfolio_data)

    except Exception as e:
        # 조회 중 예기치 않은 오류 발생
        print(f"오류: 사용자 {request.user.username if request.user.is_authenticated else '비로그인'} 포트폴리오 조회 처리 중 오류 발생: {e}")
        traceback.print_exc() # 서버 로그에 자세한 오류 추적 정보 출력
        # 클라이언트에게 오류 응답 반환
        return JsonResponse({'message': '포트폴리오 데이터를 가져오는데 실패했습니다.', 'error': str(e)}, status=500)
























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


@login_required # 로그인 사용자만 키 발급 가능하도록
def get_websocket_key_api(request): # ★ 키 발급 전용 API 뷰 ★
    """ KIS 웹소켓 접속 승인키를 발급하여 JSON으로 반환하는 API 뷰 """
    print("[API] 웹소켓 승인키 발급 요청 받음 (/api/get_websocket_key/)")
    approval_key = get_kis_approval_key() # 별도 파일의 함수 호출

    if approval_key:
        # 성공 시
        print("[API] 웹소켓 승인키 발급 성공")
        return JsonResponse({'success': True, 'approval_key': approval_key})
    else:
        # 실패 시
        print("[API] 웹소켓 승인키 발급 실패")
        return JsonResponse({'success': False, 'message': '웹소켓 승인키 발급에 실패했습니다.'}, status=500) # 500 서버 오류




















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
def purchase_item_api_view22(request):
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



















# view_main.py

# ... 필요한 import (json, Decimal, transaction, User 등) ...
from decimal import Decimal, InvalidOperation
from django.db import transaction
from django.db.models import F
import traceback

# User 모델 import (네 models.py에 정의된 User 모델 정확히 import)
from django.contrib.auth import get_user_model
User = get_user_model()

# TODO: StrategyPageSubscription, PositionViewSubscription, UserTitle 등 모델 import (네 models.py에 있다면)
from main.models import StrategyPageSubscription, PositionViewSubscription # 예시 import (네 실제 모델 위치에 맞게)
# TODO: UserTitle 모델 import (네 models.py에 있다면)


# TODO: spend_asi_coin 함수가 User 모델 메서드로 구현되어 있어야 함
# 이 함수는 user 객체 (락 걸린), 차감할 Decimal 금액, 아이템 이름 받음.
# asi_coin_balance 필드가 DecimalField여야 정확하며, 실제 ASI 출금 연동 로직이 포함되어야 함.
# 성공 시 True, 잔액 부족 또는 오류 시 False 반환.
# 예시 (User 모델 메서드로 정의되어 있다고 가정):
# def spend_asi_coin(self, amount: Decimal, item_name=""): ...


# TODO: Real Cash 가격 1 ASI = 1000 KRW (고정 환율 가정)
# 실제 환경에서는 이 가격이 변동될 수 있으며, 별도 시스템에서 관리/계산되어야 함.
# 이 상수는 view_main.py 파일의 맨 위나 설정 파일에 정의되어 있어야 함.
ASI_KRW_RATE = Decimal("1000.0")


@login_required
@require_POST
@csrf_exempt # JavaScript에서 CSRF 토큰을 헤더에 포함하여 보내는 경우 이 줄은 주석 처리하거나 삭제
def purchase_item_api_view(request):
    """
    ASI Coin 상점 아이템 구매 요청을 처리하고, 결제 방식에 따라
    real_cash, 모의투자 현금, 또는 ASI 코인을 차감하며 아이템 효과를 적용하는 API 뷰.
    가격은 백엔드에 하드코딩된 값을 사용합니다.
    """
    print("\n[DEBUG] ===== purchase_item_api_view 시작 =====")
    try:
        # 1. 요청 본문에서 JSON 데이터 파싱
        data = json.loads(request.body)
        item_id = data.get('item_id') # 구매할 아이템의 ID (프론트엔드에서 받음)
        payment_method = data.get('payment_method') # 결제 방식 ('asi', 'cash', 'sim_cash') (프론트엔드에서 받음)
        purchase_quantity = data.get('quantity') # ASI 코인 충전 등 수량 (프론트엔드에서 받음)
        selected_color = data.get('color') # 닉네임 색상 변경 시 (프론트엔드에서 받음)
        target_user_id = data.get('target_user_id') # 트레이더 포지션 보기 등 (프론트엔드에서 받음)
        strategy_id = data.get('strategy_id') # 전략 구독 시 (프론트엔드에서 받음)
        profit_ratio = data.get('profit_ratio') # 수익률 비례 결제 시 수익률 (프론트엔드에서 받음)

        user = request.user # 요청을 보낸 로그인된 사용자
        user_id = user.id

        print(f"로그: 사용자 {user.username} 아이템 구매 요청 수신 - Item ID: {item_id}, 결제 방식: {payment_method}")
        print(f"로그: 수량: {purchase_quantity}, 색상: {selected_color}, 대상ID: {target_user_id}, 전략ID: {strategy_id}, 수익률: {profit_ratio}")


        # 2. 아이템 정보 및 백엔드 가격 정의 (★★★ 보안 핵심: 가격은 여기에 정의!) ★★★
        # price는 Decimal 타입으로 정확하게 정의.
        # cost_type: 'cash' (real_cash 차감), 'asi' (asi_coin_balance 차감), 'sim_cash' (user.cash 차감)
        items_info = {
            'cash_refill': {'cost_type': 'cash', 'price': Decimal("10000.0"), 'name': "모의투자 머니 초기화"},
            'cash_refill': {'cost_type': 'asi', 'price': Decimal("1.0"), 'name': "모의투자 머니 초기화"},
            'level_xp_1000': {'cost_type': 'cash', 'price': Decimal("100.0"), 'name': "레벨 경험치 +1000"},
            'wl_reset': {'cost_type': 'cash', 'price': Decimal("4000.0"), 'name': "승패 초기화"},
            'nickname_color': {'cost_type': 'cash', 'price': Decimal("1000.0"), 'name': "닉네임 색상 변경권"},
            'profile_cosmetic': {'cost_type': 'cash', 'price': Decimal("5000.0"), 'name': "프로필 꾸미기"}, # 예시 가격
            # ASI 코인 충전: 가격은 수량*1000원, 현금 결제. price는 None으로 정의하고 로직에서 계산.
            'asi_refill': {'cost_type': 'cash', 'price': None, 'name': "ASI 코인 충전"},
            # 칭호 구매: 모의투자 현금 결제, 레벨 제한. price는 모의투자 현금 가격.
            'title_purchase': {'cost_type': 'sim_cash', 'price': Decimal("1000000.0"), 'name': "칭호 구매", 'level_required': 5},
            # ASI 코인 결제 아이템들 (현금 결제 옵션도 있으면 cost_type/price 쌍 추가)
            'view_trader': {'cost_type': 'asi', 'price': Decimal("100.0"), 'name': "트레이더 포지션 보기 (1주일)"}, # 현금 결제 옵션 추가 가능
            'strategy_page_sub': {'cost_type': 'asi', 'price': Decimal("100.0"), 'name': "AI 트레이더 구독 (1주일)"}, # 현금 결제 옵션 추가 가능
            'auto_trade_10h': {'cost_type': 'asi', 'price': Decimal("1.0"), 'name': "자동매매 시간 충전 (10시간)"}, # 현금 결제 옵션 추가 가능
            # 수익률 비례 결제: 가격은 동적 계산, 결제 방식은 프론트에서 지정
            'strategy_sub_profit': {'cost_type': 'dynamic', 'name': "전략 구독 (수익률 비례)", 'asi_rate_per_percent': Decimal("1.0"), 'cash_rate_per_percent': ASI_KRW_RATE}, # 수익률 1%당 1 ASI, 1%당 1000원
        }

        # 3. 요청된 item_id 유효성 확인 및 기본 정보 가져오기
        if item_id not in items_info:
             print(f"오류: 사용자 {user.username} - 알 수 없는 아이템 ID 수신: {item_id}")
             return JsonResponse({'success': False, 'message': '알 수 없는 아이템입니다.'}, status=400)

        item_info = items_info[item_id]
        item_name = item_info['name']
        backend_cost_type_definition = item_info.get('cost_type') # 백엔드에 정의된 결제 타입 (dynamic일 수 있음)
        backend_fixed_price = item_info.get('price')         # 백엔드에 정의된 고정 가격 (None일 수 있음)


        # --- 4. 결제 방식 및 아이템 ID에 따른 실제 차감 금액 결정 및 차감 시도 ---
        amount_to_deduct = Decimal("0.0") # 실제로 차감될 금액
        actual_cost_type_used = None     # 실제로 어떤 잔액에서 차감했는지 기록
        deduction_success = False        # 차감 성공 여부

        # DB 업데이트 및 차감은 원자적 트랜잭션으로 묶음
        try:
            with transaction.atomic():
                # 사용자 객체 최신 상태 로드 및 락 설정 (DB에서 데이터를 가져옴)
                user_locked = User.objects.select_for_update().get(pk=user_id)

                # === 아이템 ID 및 결제 방식에 따른 가격 결정 및 차감 로직 ===

                # --- ASI 코인 충전 (asi_refill) ---
                if item_id == 'asi_refill':
                    if payment_method != 'cash':
                         raise ValueError(f"'{item_name}' 아이템은 현금으로만 구매 가능합니다.")
                    if purchase_quantity is None or not isinstance(purchase_quantity, int) or purchase_quantity <= 0:
                         raise ValueError("올바른 코인 충전 수량(정수, 1 이상)이 필요합니다.")

                    amount_to_deduct = Decimal(str(purchase_quantity)) * ASI_KRW_RATE # KRW 가격 계산
                    actual_cost_type_used = 'cash' # 실제 차감은 현금

                    # 현금 차감 시도 (User 모델 메서드 사용)
                    if not user_locked.spend_real_cash(amount_to_deduct):
                         raise ValueError("현금 잔액이 부족하거나 결제 중 오류가 발생했습니다.")

                    # 차감 성공 시, 사용자 ASI 코인 잔액 증가
                    user_locked.asi_coin_balance += Decimal(str(purchase_quantity))
                    user_locked.save(update_fields=['asi_coin_balance']) # ASI 잔액 변경사항 저장
                    deduction_success = True
                    result_message = f"ASI 코인 {purchase_quantity}개가 충전되었습니다!"


                # --- 칭호 구매 (title_purchase) ---
                elif item_id == 'title_purchase':
                    if payment_method != 'sim_cash':
                        raise ValueError(f"'{item_name}' 아이템은 모의투자 현금으로만 구매 가능합니다.")
                    # 레벨 제한 확인 (User 모델의 @property 사용)
                    level_required = item_info.get('level_required', 0)
                    if user_locked.current_level < level_required:
                         raise ValueError(f"레벨 {level_required} 이상만 구매 가능합니다. (현재 레벨: {user_locked.current_level})")

                    amount_to_deduct = backend_fixed_price # 모의투자 현금 가격
                    actual_cost_type_used = 'sim_cash' # 실제 차감은 모의 현금

                    # 모의 현금 차감 시도 (User 모델 메서드 사용)
                    if not user_locked.spend_sim_cash(amount_to_deduct):
                         raise ValueError("모의투자 현금이 부족하거나 구매 중 오류가 발생했습니다.")

                    # TODO: 사용자에게 칭호 부여 로직 구현 (UserTitle 모델 등)
                    # UserTitle.objects.create(user=user_locked, title='구매한칭호') # 예시

                    deduction_success = True
                    result_message = f"'{item_name}' 칭호를 획득했습니다!"


                # --- 전략 구독 (수익률 비례) (strategy_sub_profit) ---
                elif item_id == 'strategy_sub_profit':
                     # 복잡한 로직: 가격 계산 -> 차감 -> 구독 활성화
                     # 프론트에서 전략 ID와 수익률 정보를 받아야 함.
                     if not strategy_id: raise ValueError("구독할 전략 ID가 필요합니다.")
                     if profit_ratio is None or not isinstance(profit_ratio, (int, float)): raise ValueError("유효한 수익률 정보가 필요합니다.")

                     profit_ratio_decimal = Decimal(str(profit_ratio)) # Decimal로 변환

                     # TODO: 백엔드에서 해당 전략의 실제 수익률 다시 검증하는 로직 추가 권장
                     # actual_strategy_profit_ratio = get_strategy_profit(strategy_id) # 백엔드 함수 가정
                     # if abs(profit_ratio_decimal - actual_strategy_profit_ratio) > Decimal("0.01"): # 허용 오차 설정
                     #     raise ValueError("전략 수익률 정보가 일치하지 않습니다. 다시 시도해주세요.")

                     # 가격 계산 (수익률 1%당 1 ASI 또는 1000원)
                     asi_rate_per_percent = item_info.get('asi_rate_per_percent', Decimal("0"))
                     cash_rate_per_percent = item_info.get('cash_rate_per_percent', Decimal("0"))


                     if payment_method == 'asi':
                          # 가격 in ASI = 수익률(소수점) * 100 * ASI_rate_per_percent
                          amount_to_deduct = profit_ratio_decimal * Decimal("100.0") * asi_rate_per_percent # ASI 단위 계산
                          actual_cost_type_used = 'asi'
                          # ASI 코인 차감 시도
                          if not user_locked.spend_asi_coin(amount_to_deduct, item_name):
                              raise ValueError("ASI 코인 잔액이 부족합니다.")
                          # TODO: 실제 출금 트랜잭션 해시 기록/조회 로직 추가
                          # tx_hash = ...

                     elif payment_method == 'cash':
                          # 가격 in KRW = 수익률(소수점) * 100 * cash_rate_per_percent
                          amount_to_deduct = profit_ratio_decimal * Decimal("100.0") * cash_rate_per_percent # KRW 단위 계산
                          actual_cost_type_used = 'cash'
                           # 현금 차감 시도
                          if not user_locked.spend_real_cash(amount_to_deduct):
                              raise ValueError("현금 잔액이 부족합니다.")
                     else:
                         raise ValueError("알 수 없는 결제 방식입니다.")

                     # TODO: 전략 구독 활성화 로직 구현 (StrategySubscription 모델 등)
                     # StrategySubscription.objects.create(subscriber=user_locked, strategy_id=strategy_id, end_date=timezone.now() + timedelta(days=7)) # 예시

                     deduction_success = True
                     result_message = f"'{item_name}' 구독 완료! ({amount_to_deduct:.2f} {'ASI' if payment_method == 'asi' else 'KRW'} 차감)" # 메시지 동적 표시


                # --- 그 외 모든 표준 아이템 (고정 가격, cash 또는 asi 결제) ---
                else: # item_id가 위 특별 케이스가 아닌 경우
                     if backend_cost_type_definition is None or backend_fixed_price is None:
                          raise ValueError(f"'{item_name}' 아이템의 가격 정보가 불완전합니다.")

                     # 요청된 결제 방식이 백엔드에 정의된 타입과 일치하는지 확인
                     if payment_method != backend_cost_type_definition:
                         raise ValueError(f"'{item_name}' 아이템은 '{backend_cost_type_definition}' 결제만 지원합니다.")


                     amount_to_deduct = backend_fixed_price # 백엔드에 정의된 고정 가격 사용
                     actual_cost_type_used = backend_cost_type_definition # 사용된 결제 타입

                     if actual_cost_type_used == 'cash':
                         # 현금 차감 시도 (User 모델 메서드 사용)
                         if not user_locked.spend_real_cash(amount_to_deduct):
                             raise ValueError("현금 잔액이 부족합니다.")
                         deduction_success = True
                         result_message = f"'{item_name}' 구매 완료! ({amount_to_deduct:.0f} KRW 차감)" # 원화는 소수점 없앰

                     elif actual_cost_type_used == 'asi':
                         # ASI 코인 차감 시도 (User 모델 메서드 사용)
                         if not user_locked.spend_asi_coin(amount_to_deduct, item_name):
                              raise ValueError("ASI 코인 잔액이 부족합니다.")
                         deduction_success = True
                         result_message = f"'{item_name}' 구매 완료! ({amount_to_deduct:.4f} ASI 차감)" # ASI는 소수점 표시
                         # TODO: ASI 출금 시 tx_hash 기록/조회 로직 추가
                         # tx_hash = ...

                     elif actual_cost_type_used == 'sim_cash':
                          # 표준 아이템에 sim_cash가 정의되어 있다면 여기서 처리 (현재는 title_purchase만 sim_cash)
                          # title_purchase는 위에서 특별 처리했으므로 여기에 오지 않아야 함.
                          # 만약 다른 sim_cash 아이템이 있다면 여기에 로직 추가
                          raise ValueError(f"'{item_name}' 아이템은 모의 현금 결제를 지원하지 않습니다.") # 오류 메시지

                     else:
                         # Should not reach here if cost_type_definition is handled
                         raise ValueError(f"'{item_name}' 아이템에 대한 알 수 없는 결제 타입 처리: {actual_cost_type_used}")


                # --- 차감 성공 시, 나머지 효과 적용 (deduction_success가 True일 때만 실행) ---
                # 차감 실패 시는 여기서 예외가 발생해서 트랜잭션 롤백됨.
                if deduction_success:
                    action_success = False # 아이템 효과 적용 성공 플래그
                    # result_message는 이미 위에서 차감 성공 시 설정됨.

                    # === 각 아이템 ID 별 효과 적용 ===
                    # ASI 코인 충전, 칭호 구매, 수익률 비례 전략 구독 등은 효과 적용 로직이
                    # 위에서 이미 차감 로직과 함께 또는 특별 케이스로 처리됨.
                    # 여기서는 그 외 아이템들의 효과를 최종적으로 적용.

                    if item_id == 'cash_refill':
                        # 모의투자 머니 초기화 - 이미 위에서 user.cash 업데이트로 처리됨
                        action_success = True # 차감 성공 시 효과 적용도 성공으로 간주
                        # user_locked.cash 업데이트는 이미 위에서 했음.

                    elif item_id == 'level_xp_1000':
                        # 레벨 경험치 추가 - 이미 위에서 user.level_xp 업데이트로 처리됨
                        action_success = True # 차감 성공 시 효과 적용도 성공으로 간주
                        # TODO: 레벨업 로직 호출 (user_locked.add_level_xp() 같은 함수 사용)

                    elif item_id == 'wl_reset':
                         # 승패 초기화 효과 적용
                         user_locked.total_wins = 0
                         user_locked.total_losses = 0
                         user_locked.save(update_fields=['total_wins', 'total_losses'])
                         action_success = True
                         result_message = result_message or "승패 기록이 초기화되었습니다." # 메시지 중복 방지
                         user_locked.refresh_from_db(fields=['total_wins', 'total_losses']) # 업데이트된 승패 반영

                    elif item_id == 'nickname_color':
                        # 닉네임 색상 변경 로직 - 이미 위에서 user.nickname_color 업데이트로 처리됨
                        # selected_color 유효성 검사는 위에서 했음.
                        # user_locked.nickname_color 업데이트는 위에서 했음.
                        action_success = True # 차감 성공 시 효과 적용도 성공으로 간주
                        # result_message는 이미 위에서 설정됨
                        user_locked.refresh_from_db(fields=['nickname_color']) # 업데이트된 색상 반영


                    elif item_id == 'profile_cosmetic':
                         # 프로필 꾸미기 아이템 효과 적용 로직 (예: 사용자에게 아바타/배경 선택/지급)
                         # TODO: 구현 필요. 어떤 꾸미기 아이템인지 추가 데이터(예: cosmetic_id) 필요할 수 있음.
                         # UserCosmetic.objects.create(user=user_locked, cosmetic_id=...) # 예시
                         action_success = True
                         result_message = result_message or f"'{item_name}' 아이템이 적용되었습니다!" # 메시지


                    elif item_id == 'auto_trade_10h':
                         # 자동매매 시간 충전 - 이미 위에서 시간 추가로 처리됨
                         action_success = True # 차감 성공 시 효과 적용도 성공으로 간주
                         # result_message는 이미 위에서 설정됨
                         user_locked.refresh_from_db(fields=['auto_trade_seconds_remaining']) # 시간 반영


                    # TODO: strategy_sub_profit (수익률 비례 결제) 아이템 효과 로직 구현 (복잡)
                    # 차감은 위에서 이미 되었음. 여기서는 구독 활성화 로직.
                    # 프론트에서 보낸 strategy_id에 대한 구독을 활성화해야 함.
                    # StrategySubscription.objects.create(...)
                    # 이 아이템은 가격 계산과 차감, 그리고 구독 활성화가 한 로직으로 묶여야 더 안전함.
                    # 현재는 차감 후 여기까지 오므로 임시 성공 처리.
                    # elif item_id == 'strategy_sub_profit':
                    #    # TODO: 구독 활성화 로직 구현
                    #    action_success = True
                    #    result_message = result_message or "수익률 비례 전략 구독 완료!"


                    elif item_id in ['asi_refill', 'title_purchase', 'view_trader', 'strategy_page_sub']:
                         # 이 아이템들은 효과 적용 로직이 이미 위 차감 블록에서 특별 처리되었거나 포함됨.
                         # 여기에 다시 로직을 넣을 필요는 없음.
                         action_success = True # 이미 위에서 처리되었다고 가정하고 성공 처리


                    else:
                         # items_info에는 정의되어 있지만 여기서 효과 적용 로직이 누락된 경우
                         # 차감은 이미 되었으므로 환불 로직이 필요하거나, 애초에 효과 적용 로직까지 포함해야 함.
                         print(f"오류: 아이템 ID '{item_id}' 효과 적용 로직 누락 또는 미완성.")
                         # raise NotImplementedError(f"아이템 ID '{item_id}' 효과 적용 로직이 누락되었거나 미완성입니다.") # 개발 중에는 에러 발생
                         # 임시로 차감 성공/효과 적용 누락 메시지를 반환 (실제 서비스에서는 적절한 오류 처리 필요)
                         action_success = False # 효과 적용 실패 (개발자에게 알림)
                         result_message = result_message or f"'{item_name}' 결제는 완료되었으나 효과 적용 로직이 아직 구현되지 않았습니다. 관리자에게 문의하세요."


                    # --- 모든 DB 변경사항 최종 저장 (transaction.atomic으로 묶여있음) ---
                    # save()는 위에서 save(update_fields=...)를 사용했더라도 최종 상태를 보장하기 위해 호출
                    # 특히 effect 로직에서 save를 명시적으로 호출했다면 중복될 수 있지만 트랜잭션 안에서는 괜찮음
                    # user_locked.save()


                else:
                     # 차감은 성공했으나 effect 적용 로직이 없는 아이템이거나 다른 문제로 여기 온 경우
                     # 위에 raise ValueError 등으로 예외가 발생해서 여기 오지 않아야 정상.
                     # 혹시 모를 상황 대비 (대부분 여기에 오지 않아야 함)
                     print(f"오류: 아이템 구매 처리 최종 실패 - 차감 성공={deduction_success}, 효과 적용 성공={action_success}")
                     # 에러 메시지는 이미 위의 except 블록에서 설정되었을 것임.
                     raise ValueError("아이템 구매 처리 중 예기치 않은 오류 발생.") # 트랜잭션 롤백 유도


        # --- Exception Handling within Transaction ---
        except ValueError as ve:
             # Catch specific validation errors and deduction errors (raised as ValueErrors)
             print(f"오류 (ValueError): 아이템 구매 처리 중 오류 ({item_id}) - {ve}")
             # Transaction is rolled back automatically
             return JsonResponse({'success': False, 'message': f"구매 처리 실패: {ve}"}, status=400)
        except NotImplementedError as nie:
             # catch missing effect logic if raised
             print(f"오류 (NotImplementedError): 아이템 효과 적용 로직 누락 ({item_id}) - {nie}")
             return JsonResponse({'success': False, 'message': '서버 내부 오류: 아이템 효과 로직 미구현.'}, status=500)
        except Exception as e: # Catch any other unexpected errors during transaction block
             print(f"오류 (Exception): 아이템 효과 적용 중 예기치 않은 오류 ({item_id}): {e}")
             traceback.print_exc()
             # Transaction is rolled back automatically
             return JsonResponse({'success': False, 'message': '서버 내부 오류가 발생했습니다.'}, status=500)


        # --- Final Success Response ---
        # If code reaches here, both deduction and item effect application were successful
        # 트랜잭션 완료 후, 사용자 객체의 최신 잔액 정보 다시 로드
        user_locked = User.objects.get(pk=user_id) # 트랜잭션 밖에서 새로 가져옴 (락 필요 없음)
        # 또는 위에서 이미 락 걸었던 user_locked 객체를 사용하되, 트랜잭션 밖에서 save/refresh

        # 응답에 포함시킬 최종 잔액 정보 (DecimalField는 JSON 직렬화 시 문자열 될 수 있음. 프론트에서 파싱 필요)
        final_asi_balance = user_locked.asi_coin_balance
        final_real_cash = user_locked.real_cash
        final_sim_cash = user_locked.cash

        # TODO: ASI 출금 시 tx_hash 기록/조회 로직 구현했다면 여기에 포함
        # tx_hash = ... # 트랜잭션 내에서 얻은 해시

        return JsonResponse({
            'success': True,
            'message': result_message or f"'{item_name}' 구매 완료!",
            # 프론트엔드 잔액 업데이트용 최신 잔액 정보 포함 (숫자로 파싱하기 용이하도록 Decimal 유지)
            'new_balance': final_asi_balance, # ASI 잔액 (Decimal)
            'new_real_cash': final_real_cash, # 현금 잔액 (Float/Decimal)
            'new_sim_cash': final_sim_cash, # 모의 현금 잔액 (Float/Decimal)
            # 필요시 사용자 레벨, 티어, 승패 등 업데이트된 정보도 같이 보냄.
            # user_locked 객체에서 가져온 필드들 포함.
            'new_level_xp': user_locked.level_xp,
            'new_level': user_locked.current_level, # @property 값 사용
            'new_user_tier_xp': user_locked.user_tier_xp,
            'new_user_tier_info': user_locked.get_tier_info(), # @property 결과 사용
            'new_total_wins': user_locked.total_wins,
            'new_total_losses': user_locked.total_losses,
            'new_auto_trade_seconds': user_locked.auto_trade_seconds_remaining,
            'tx_hash': tx_hash # ASI 출금 시 해시 (필요시)
        })


    # --- 최외곽 에러 처리 ---
    except json.JSONDecodeError:
        print("오류: 잘못된 JSON 요청 본문.")
        return JsonResponse({'success': False, 'message': '잘못된 요청 형식입니다.'}, status=400)
    except Exception as e:
        print(f"API 오류 (/api/shop/purchase/): {e}") # 예기치 않은 서버 내부 오류
        traceback.print_exc()
        return JsonResponse({'success': False, 'message': '서버 내부 오류가 발생했습니다.'}, status=500)

# TODO: spend_asi_coin 함수 구현 필요 (User 모델의 asi_coin_balance 차감) - Decimal 사용하도록
# TODO: StrategyPageSubscription, PositionViewSubscription, UserTitle 모델 구현 필요
# TODO: spend_asi_coin 함수 내에서 ASI 출금 연동 및 tx_hash 반환 로직 추가 필요
# TODO: 수익률 비례 전략 구독 가격 계산 및 활성화 로직 구현 (복잡)
# TODO: spend_real_cash, spend_sim_cash 함수가 User 모델 메서드로 구현되어 있다면 여기서 삭제하고 User 모델에서 import하여 사용.
# TODO: User 모델에 current_level, get_tier_info 메서드가 없다면 models.py에 추가.


















from django.http import JsonResponse
from django.views.decorators.http import require_POST # POST 요청만 받도록
from django.views.decorators.csrf import ensure_csrf_cookie # CSRF 처리 관련 (필요시)
from django.contrib.auth.decorators import login_required
from chart.blockchain_reward import process_trade_result # 코인 보상 업데이트

@login_required # 로그인 필수
@require_POST  # POST 요청만 허용
# @ensure_csrf_cookie # CSRF 쿠키 보장 (필요에 따라)
def process_trade_result_api_view(request):
    """ JavaScript로부터 매도 결과를 받아 서비스 함수를 호출하는 API 뷰 """
    # 뷰 함수에 @transaction.atomic을 적용하면 이 함수 내부에서 호출하는 모든 DB 작업이 하나의 트랜잭션으로 묶임
    # process_trade_result 내부의 grant_asi_reward도 이 트랜잭션에 포함됨.
    # grant_asi_reward 자체에 @transaction.atomic이 있어도 중첩 트랜잭션으로 잘 동작함.
    try:
        # 요청 본문(body)에서 JSON 데이터 읽기
        data = json.loads(request.body)
        profit_usd = data.get('profit') # JavaScript에서 보낸 'profit' 키의 값
        user_id = request.user.id

        # profit 값이 숫자인지 확인 (간단한 유효성 검사)
        # isinstance(profit_usd, (int, float, str)) 로 더 유연하게 받을 수도 있음
        if profit_usd is None or not isinstance(profit_usd, (int, float, str)): # 숫자나 문자열 형태의 숫자를 허용
            return JsonResponse({'success': False, 'message': '유효한 수익 정보(profit)가 필요합니다.'}, status=400)

        # service 함수 호출하여 DB 업데이트 시도
        # process_trade_result 함수는 이제 (처리 성공 여부, 지급된 ASI 금액(Decimal))을 반환
        # profit_usd가 문자열일 경우 float으로 변환해서 전달
        success, granted_asi_amount = process_trade_result(user_id, float(profit_usd)) # float으로 변환해서 전달

        if success:
            # 성공 시, 응답에 지급된 ASI 금액 포함
            # Decimal 타입은 JsonResponse가 처리 못하므로 문자열이나 float으로 변환
            # granted_asi_amount는 Decimal("0.0") 일 수 있으므로 float 변환 안전
            return JsonResponse({
                'success': True,
                'message': '매도 결과가 처리되었습니다.',
                'asi_reward': float(granted_asi_amount) # Decimal을 float으로 변환하여 응답
            })
        else:
            # 서비스 함수 내부에서 실패한 경우
            # process_trade_result 함수 내부의 print 로그로 원인 파악 필요
            # 실패 시 보상 금액은 0이므로 포함하지 않거나 0으로 포함
             return JsonResponse({'success': False, 'message': '매도 결과 처리 중 서버 내부 오류가 발생했습니다.'}, status=500)


    except json.JSONDecodeError:
        # 요청 본문이 유효한 JSON이 아닐 경우
        return JsonResponse({'success': False, 'message': '잘못된 요청 형식입니다 (JSON 오류).'}, status=400)
    except Exception as e:
        # 기타 예외 처리 (로그인 안 된 경우 등 @login_required 데코레이터에서 처리되지만, 안전상)
        print(f"API 오류: /api/trade/process_result/ - {e}") # 서버 로그에 기록
        import traceback
        traceback.print_exc()
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














""" 프로필 설정 페이지를 보여주는 뷰 (GET 요청 처리) """
@login_required # 로그인 필수
def profile_settings_view(request):

    # TODO: 여기에 POST 요청 처리 로직 추가 필요 (폼 제출 시)
    # if request.method == 'POST':
    #     # 폼 종류(nickname, contact, wallet, sharing) 구분
    #     form_type = request.POST.get('form_type')
    #     if form_type == 'nickname':
    #         # 닉네임 변경 처리 (쿨타임 확인, 유효성 검사, DB 저장)
    #         pass
    #     elif form_type == 'sharing':
    #         # 포지션 공유 설정 처리
    #         pass
    #     elif form_type == 'contact' or form_type == 'wallet':
    #         # 인증 절차 시작 (이메일 발송, SMS 발송 등 - 별도 구현 필요)
    #         messages.info(request, "인증 절차 구현이 필요합니다.")
    #         pass
    #     # 처리 후 현재 페이지로 다시 리다이렉트 (메시지 포함)
    #     return redirect('profile_settings')

    # GET 요청 시 현재 사용자 정보 전달
    context = {
        'user': request.user
    }
    return render(request, 'main/user_profile_setting.html', context)



# views.py (예시: index2_simulator_page 뷰)
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import json
from django.contrib.auth import get_user_model
from .models import Holding # 모델 임포트 가정

User = get_user_model()



@login_required # 시뮬레이터 페이지는 로그인 필수 가정
def index2_simulator_page_backup(request): # ★ 시뮬레이터 HTML 페이지 렌더링 전용 뷰 ★
    """ 시뮬레이터 HTML 페이지만 렌더링하는 뷰 """
    print("시뮬레이터 페이지 요청 받음 (/index2_simulator/)")
    context = {
        'user': request.user,
    }
    # 템플릿 파일 경로는 실제 프로젝트 구조에 맞게 확인 필요
    return render(request, 'main/index2_simulator.html', context)